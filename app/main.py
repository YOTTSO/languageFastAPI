import json

from fastapi import FastAPI, Request, UploadFile, Depends, File, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from analyzer import Analyzer
from crud import create_text, get_text, get_text_by_id, set_buffer, get_current_table
from database import SessionLocal, sync_engine, Base
from schemas import Text, CurrentTable

Base.metadata.create_all(bind=sync_engine)

app = FastAPI(debug=True)
buffer = ""

def get_db():
    db =SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates("templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.post("/upload")
def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    def save_file(text: Text, db: Session):
        create_text(db=db, text=text)
        return None

    analyzer = Analyzer()
    text = Text(name=file.filename, raw_text=file.file.read())
    current_table = CurrentTable(name=text.name)
    set_buffer(db=db, current_table=current_table)
    text.tokens = analyzer.leksems(text.raw_text)
    text.collocations = analyzer.analyze(text.raw_text)
    save_file(text=text, db=db)
    return text.name


@app.get("/get_data")
def get_data(db: Session = Depends(get_db)):
    current_table = get_current_table(db)[0]
    text = get_text_by_id(db=db, name=current_table.name)
    return [text]




