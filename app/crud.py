from sqlalchemy import text, select
from sqlalchemy.orm import Session
from app.schemas import Text, CurrentTable
from app.models import TextsOrm, CurrentTableOrm


def create_text(db: Session, text: Text):
    texts = get_text(db)
    texts_name = [i.name for i in texts]
    if text.name not in texts_name:
        text_db = TextsOrm(**text.model_dump())
        db.add(text_db)
        db.commit()
    else:
        text_db_new = TextsOrm(**text.model_dump())
        text_db = get_text_by_id(db=db, name=text.name)[0]
        text_db.raw_text = text_db_new.raw_text
        text_db.collocations = text_db_new.collocations
        text_db.tokens = text_db_new.tokens
        db.commit()


def get_text(db: Session):
    result = []
    try:
        texts = (db.query(TextsOrm).all())
        for item in texts:
            result.append(Text.model_validate(item))
        return result
    except Exception as e:
        raise e


def set_buffer(db: Session, current_table: CurrentTable):
    current_tables = get_current_table(db)
    if current_tables is not None:
        if current_table not in current_tables:
            db.execute(text("DELETE FROM current_table"))
            current_table_orm = CurrentTableOrm(**current_table.model_dump())
            db.add(current_table_orm)
            db.commit()
    else:
        current_table_orm = CurrentTableOrm(**current_table.model_dump())
        db.add(current_table_orm)
        db.commit()


def get_current_table(db: Session):
    table = db.query(CurrentTableOrm).first()
    if table is not None:
        return CurrentTable.model_validate(table)
    else:
        return None


def get_text_by_id(db: Session, name: str):
    text = db.query(TextsOrm).filter(TextsOrm.name == name).one() if not None else None
    return [Text.model_validate(text)]

# def insert_data():
#     with SessionLocal() as session:
#         session.add()
#
#
# def select_data():
#     with SessionLocal() as session:
#         return session.query(TextsOrm).all()
