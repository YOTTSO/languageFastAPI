import asyncio
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, URL, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from config import settings

sync_engine = create_engine(
    url=settings.db_url,
    echo=False
)

async_engine = create_async_engine(
    url=settings.db_url,
    echo=False
)

SessionLocal = sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=sync_engine)
async_session_factory = async_sessionmaker(async_engine,  expire_on_commit=False, class_=AsyncSession)


# def get_session() -> Generator[Session, None]:
#     with session_factory as session:
#         yield session
#
#
# def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     with async_session_factory as async_session:
#         yield async_session


class Base(DeclarativeBase):
    pass
