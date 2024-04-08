from sqlalchemy import create_engine
import sqlalchemy.orm as _orm
from config import settings


engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False
)

SessionLocal = _orm.sessionmaker(expire_on_commit=False, autocommit=False, autoflush=True, bind=engine)


class Base(_orm.DeclarativeBase):
    pass