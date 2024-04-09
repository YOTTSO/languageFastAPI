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


class XmlText(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = None
    filename: str
    author: str | None = None
    tags: str | None = None
    markup: str | None = None
    raw_text: str | None = None


class CurrentTable(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
