from sqlalchemy import text
from sqlalchemy.orm import Session
from app.schemas import Text, CurrentTable, XmlText
from app.models import TextsOrm, CurrentTableOrm, XmlTextOrm


def create_text(db: Session, text_new: Text):
    texts = get_text(db)
    texts_name = [i.name for i in texts]
    if text_new.name not in texts_name:
        text_db = TextsOrm(**text_new.model_dump())
        db.add(text_db)
        db.commit()
    else:
        text_db = db.query(TextsOrm).filter(TextsOrm.name == text_new.name).one()
        text_db.raw_text = text_new.raw_text
        text_db.collocations = text_new.collocations
        text_db.tokens = text_new.tokens
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
    texts = db.query(TextsOrm).filter(TextsOrm.name == name).one() if not None else None
    return [Text.model_validate(texts)]

class DBCorpusManager:
    def create_xml(self, xml: XmlText, db: Session):
        xml_texts = [i.filename for i in self.read_all_xml(db)]
        if xml.filename not in xml_texts:
            xml_db = XmlTextOrm(**xml.model_dump())
            db.add(xml_db)
            db.commit()
        elif xml in xml_texts:
            self.update_xml(xml, db)

    def update_xml(self, new_xml: XmlText, db: Session):
        old_xml = db.query(XmlTextOrm).filter(XmlTextOrm.filename == new_xml.filename).one()
        old_xml.title = new_xml.title
        old_xml.author = new_xml.author
        old_xml.tags = new_xml.tags
        old_xml.text_markup = new_xml.text_markup
        old_xml.words_markup = new_xml.words_markup
        old_xml.raw_text = new_xml.raw_text
        db.commit()

    def read_xml(self, name: str, db: Session):
        xml_text = db.query(XmlTextOrm).filter(XmlTextOrm.filename == name).one()
        return XmlText.model_validate(xml_text)

    def read_all_xml(self, db: Session):
        xml_texts = db.query(XmlTextOrm).all()
        return [XmlText.model_validate(item) for item in xml_texts]