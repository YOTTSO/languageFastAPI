from typing import List

from sqlalchemy import Column, String, ARRAY, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TextsOrm(Base):
    __tablename__ = 'texts'

    name = Column(String, primary_key=True, index=True, nullable=False)
    raw_text = Column(String, nullable=True)
    tokens = Column(ARRAY(String), nullable=True)
    collocations = Column(ARRAY(String), nullable=True)


class XmlTextOrm(Base):
    __tablename__ = 'xml'

    title = Column(String, nullable=False, primary_key=True, index=True)
    filename = Column(String, ForeignKey('texts.name'), nullable=False)
    author = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    text_markup = Column(JSON, nullable=True)
    words_markup = Column(ARRAY(JSON), nullable=True)
    raw_text = Column(String, nullable=True)

class CurrentTableOrm(Base):
    __tablename__ = 'current_table'

    name = Column(String, nullable=False, primary_key=True)