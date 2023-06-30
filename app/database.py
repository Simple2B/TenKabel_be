from functools import lru_cache
from typing import Generator

# from alchemical.aio import Alchemical
from alchemical import Alchemical
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.config import get_settings, Settings

settings: Settings = get_settings()


engine = create_engine(settings.DATABASE_URI)

db = Alchemical(settings.DATABASE_URI, session_options={"autoflush": False})


@lru_cache
def get_engine() -> Engine:
    settings: Settings = get_settings()
    return create_engine(settings.DATABASE_URI)


def get_db() -> Generator[Session, None, None]:
    with db.Session() as session:
        yield session
