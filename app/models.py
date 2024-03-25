from sqlalchemy import Column, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TextsOrm(Base):
    __tablename__ = 'texts'

    name = Column(String, primary_key=True, index=True, nullable=False)
    raw_text = Column(String, nullable=False)
    tokens = Column(ARRAY(String), nullable=True)
    collocations = Column(ARRAY(String), nullable=True)


class CurrentTableOrm(Base):
    __tablename__ = 'current_table'

    name = Column(String, nullable=False, primary_key=True)


# class TextsOrm(Base):
#     __tablename__ = 'texts'
#
#     name: Mapped[str] = mapped_column(primary_key=True)
#     raw_text: Mapped[str]
#     tokens: Mapped[str | None]
#     collocations: Mapped[str | None]