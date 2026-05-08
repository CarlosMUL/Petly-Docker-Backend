from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from urllib.parse import quote_plus

from config import settings

password = quote_plus(settings.db_password)

_url = (
    f"postgresql+psycopg2://{settings.db_user}:{password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_engine(_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
