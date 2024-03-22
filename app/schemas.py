from typing import List

from sqlalchemy import Column, Table, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field, ConfigDict

metadata = MetaData()


class Text(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    raw_text: str
    tokens: List[str] | None = None
    collocations: List[List[str]] | None = None


class CurrentTable(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
