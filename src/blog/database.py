from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .settings import settings

engine = create_engine(
    settings.database_url,
)

Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()