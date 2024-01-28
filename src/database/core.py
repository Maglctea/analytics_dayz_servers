from typing import Iterable

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from src import settings


def get_engine() -> Engine:
    db_uri = settings.DATABASE_URL
    if not db_uri:
        raise ValueError("DB_URI env variable is not set")

    engine = create_engine(
        db_uri,
        echo=False,
        pool_size=15,
        max_overflow=15,
        connect_args={
            "connect_timeout": 5,
        },
    )
    return engine


def create_session_maker() -> sessionmaker:
    engine = get_engine()
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )


def new_session(session_maker: sessionmaker) -> Iterable[Session]:
    with session_maker() as session:
        yield session
