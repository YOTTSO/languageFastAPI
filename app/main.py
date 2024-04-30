import fastapi as _fastapi
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.analyzer import Analyzer as TextHandler, CorpusManager
from app.crud import create_text, get_text, get_text_by_id, set_buffer
from app.database import SessionLocal, engine, Base
from app.schemas import Text, CurrentTable
from app.llm_api import get_synonyms, get_antonyms, chatting

Base.metadata.create_all(bind=engine)
app = _fastapi.FastAPI(debug=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates("templates")
manager = CorpusManager()
handler = TextHandler()


@app.get("/", response_class=HTMLResponse)
def index(request: _fastapi.Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/texts/{text_name}", response_class=HTMLResponse)
def index(request: _fastapi.Request):
    return templates.TemplateResponse(
        request=request, name="text_page.html"
    )

@app.get("/get_info/{text_name}")
def get_data(text_name: str, db: Session = _fastapi.Depends(get_db)):
    text = get_text_by_id(db=db, name=text_name)
    if text:
        return text


@app.get("/get_texts")
def get_texts(db: Session = _fastapi.Depends(get_db)):
    return get_text(db)


@app.post("/upload")
def upload(file: _fastapi.UploadFile = _fastapi.File(...), db: Session = _fastapi.Depends(get_db)):
    text = Text(name=file.filename, raw_text=file.file.read())
    current_table = CurrentTable(name=text.name)
    set_buffer(db=db, current_table=current_table)
    text.tokens = handler.leksems(text.raw_text)
    text.collocations = handler.analyze(text.raw_text)
    create_text(text_new=text, db=db)
    return text.model_dump_json()

@app.post("/save_data")
def save_data(text: Text, db: Session = _fastapi.Depends(get_db)):
    text.tokens = handler.leksems(text.raw_text)
    text.collocations = handler.analyze(text.raw_text)
    create_text(text_new=text, db=db)

# @app.get("/generate_markup")
# def generate_markup(text_name: str, db: Session = _fastapi.Depends(get_db)):
#     text = get_text_by_id(db=db, name=text_name)
#     xml = manager.generate_xml(text)
#     manager.db_manager.create_xml(xml=xml, db=db)
#     return xml.model_dump_json()

@app.get("/texts/{text_name}/corpus")
def manager_main(text_name: str, db: Session = _fastapi.Depends(get_db)):
    if manager.db_manager.read_xml(db=db, name=text_name) is None:
        text = get_text_by_id(db=db, name=text_name)
        xml = manager.generate_xml(text)
        manager.db_manager.create_xml(xml=xml, db=db)
        return xml.model_dump_json()
    else:
        return (manager.db_manager.read_xml(db=db, name=text_name)).model_dump_json()


@app.get("/texts/{text_name}/corpus/search")
def search(text_name, tag: str, db: Session = _fastapi.Depends(get_db)):
    xml = manager.db_manager.read_xml(name=text_name, db=db)
    return manager.search(tag=tag, xml=xml)

@app.get("/texts/{text_name}/corpus/{word}")
def semantic_analys(word: str):
    synonyms = get_synonyms(word=word)
    antonyms = get_antonyms(word=word)
    return (synonyms, antonyms)

@app.get("/test")
def test(sentence: str):
    return handler.sentence_analyze(sentence)
