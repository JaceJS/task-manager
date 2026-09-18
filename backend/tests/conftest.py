from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.boards.repository import BoardRepository
from app.modules.boards.service import BoardService
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.service import TaskService

TEST_DB_SUFFIX = "_test"


def _test_database_url() -> str:
    url = make_url(get_settings().database_url)
    return url.set(database=f"{url.database}{TEST_DB_SUFFIX}").render_as_string(
        hide_password=False
    )


def _create_test_database_if_missing(url: str) -> None:
    target = make_url(url)
    admin_url = target.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            exists = connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": target.database},
            )
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{target.database}"'))
    except OperationalError as error:
        pytest.exit(
            f"Cannot connect to PostgreSQL at {admin_url.host}:{admin_url.port}.\n"
            f"Start it first with: docker compose up -d db\n\n{error}",
            returncode=1,
        )
    finally:
        admin_engine.dispose()


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = _test_database_url()
    _create_test_database_if_missing(url)

    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", url)
    command.upgrade(alembic_config, "head")

    test_engine = create_engine(url, future=True)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def board_service(session: Session) -> BoardService:
    return BoardService(session, BoardRepository(session), TaskRepository(session))


@pytest.fixture
def task_service(session: Session) -> TaskService:
    return TaskService(session, TaskRepository(session), BoardRepository(session))
