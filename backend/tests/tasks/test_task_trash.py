import pytest
from sqlalchemy import text

from app.modules.tasks.exceptions import BoardInTrash, TaskNotFound


@pytest.fixture
def board(board_service):
    return board_service.create_board("Onboarding")


def test_trash_lists_only_trashed_tasks_with_their_board_name(task_service, board):
    task_service.create_task(board.id, "Still active")
    first = task_service.create_task(board.id, "Deleted first")
    second = task_service.create_task(board.id, "Deleted second")
    task_service.delete_task(first.id)
    task_service.delete_task(second.id)

    trashed = task_service.list_trash()

    assert [(t.title, t.board_name) for t in trashed] == [
        ("Deleted second", "Onboarding"),
        ("Deleted first", "Onboarding"),
    ]
    assert all(t.deleted_at is not None for t in trashed)


def test_restore_task_puts_it_back_on_its_board(task_service, board):
    task = task_service.create_task(board.id, "Set up laptop")
    task_service.delete_task(task.id)

    restored = task_service.restore_task(task.id)

    assert restored.deleted_at is None
    assert [t.title for t in task_service.list_tasks(board.id)] == ["Set up laptop"]


def test_restore_task_is_rejected_while_its_board_is_in_trash(
    task_service, board_service, board
):
    task = task_service.create_task(board.id, "Set up laptop")
    task_service.delete_task(task.id)
    board_service.delete_board(board.id)

    with pytest.raises(BoardInTrash, match="Restore the board 'Onboarding' first"):
        task_service.restore_task(task.id)


def test_restore_task_that_is_not_in_trash_is_rejected(task_service, board):
    active = task_service.create_task(board.id, "Set up laptop")

    with pytest.raises(TaskNotFound):
        task_service.restore_task(active.id)
    with pytest.raises(TaskNotFound):
        task_service.restore_task(999999)


def test_delete_task_permanently_removes_the_row(task_service, board, session):
    task = task_service.create_task(board.id, "Set up laptop")
    task_service.delete_task(task.id)

    task_service.delete_task_permanently(task.id)

    rows = session.execute(
        text("SELECT count(*) FROM tasks WHERE id = :id"), {"id": task.id}
    ).scalar_one()
    assert rows == 0
    assert task_service.list_trash() == []


def test_delete_task_permanently_is_rejected_for_an_active_task(task_service, board):
    active = task_service.create_task(board.id, "Set up laptop")

    with pytest.raises(TaskNotFound):
        task_service.delete_task_permanently(active.id)
    assert [t.title for t in task_service.list_tasks(board.id)] == ["Set up laptop"]
