from typing import List

from sqlalchemy import Column, Table, Integer, String, MetaData
from pydantic import BaseModel, Field, ConfigDict

metadata = MetaData()


class Text(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    raw_text: str | None = None
    tokens: List[str] | None = None
    collocations: List[List[str]] | None = None


class TextMarkup(BaseModel):
    paragraphs: str | None = None
    sentences: str | None = None
    encoding: str | None = None
    version: str | None = None


class WordMarkup(BaseModel):
    word: str | None = None
    lemma: str | None = None
    gram: str | None = None
    pos: str | None = None
    synonyms: List[str] | None = None
    antonyms: List[str] | None = None


class XmlText(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = None
    filename: str
    author: str | None = None
    tags: str | None = None
    text_markup: TextMarkup | None = None
    words_markup: List[WordMarkup] | None = None
    raw_text: str | None = None


class CurrentTable(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
