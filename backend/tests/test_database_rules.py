import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.database import FOREIGN_KEY_VIOLATION, RESTRICT_VIOLATION, sqlstate_of


@pytest.fixture
def board_with_task(session):
    board_id = session.execute(
        text("INSERT INTO boards (name) VALUES ('Onboarding') RETURNING id")
    ).scalar_one()
    session.execute(
        text("INSERT INTO tasks (board_id, title) VALUES (:board_id, 'Set up laptop')"),
        {"board_id": board_id},
    )
    return board_id


def test_task_cannot_reference_a_board_that_does_not_exist(session):
    with pytest.raises(IntegrityError) as error:
        session.execute(
            text("INSERT INTO tasks (board_id, title) VALUES (999999, 'Orphan')")
        )

    assert sqlstate_of(error.value) == FOREIGN_KEY_VIOLATION


def test_board_with_task_rows_cannot_be_deleted_permanently(session, board_with_task):
    with pytest.raises(IntegrityError) as error:
        session.execute(
            text("DELETE FROM boards WHERE id = :id"), {"id": board_with_task}
        )

    assert sqlstate_of(error.value) == FOREIGN_KEY_VIOLATION


def test_board_with_active_tasks_cannot_be_moved_to_trash(session, board_with_task):
    with pytest.raises(IntegrityError) as error:
        session.execute(
            text("UPDATE boards SET deleted_at = clock_timestamp() WHERE id = :id"),
            {"id": board_with_task},
        )

    assert sqlstate_of(error.value) == RESTRICT_VIOLATION
    assert "still has active tasks" in str(error.value.orig)


def test_active_task_cannot_live_on_a_trashed_board(session):
    board_id = session.execute(
        text("INSERT INTO boards (name) VALUES ('Trashed') RETURNING id")
    ).scalar_one()
    session.execute(
        text("UPDATE boards SET deleted_at = clock_timestamp() WHERE id = :id"),
        {"id": board_id},
    )

    with pytest.raises(IntegrityError) as error:
        session.execute(
            text("INSERT INTO tasks (board_id, title) VALUES (:id, 'New task')"),
            {"id": board_id},
        )

    assert sqlstate_of(error.value) == RESTRICT_VIOLATION
    assert "is in trash" in str(error.value.orig)
