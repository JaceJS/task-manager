from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

NAMING_CONVENTION = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


engine = create_engine(get_settings().database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


UNIQUE_VIOLATION = "23505"
RESTRICT_VIOLATION = "23001"
FOREIGN_KEY_VIOLATION = "23503"


def sqlstate_of(error: Exception) -> str | None:
    return getattr(getattr(error, "orig", None), "sqlstate", None)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
