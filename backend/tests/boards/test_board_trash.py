import pytest
from sqlalchemy import text

from app.modules.boards.exceptions import BoardHasTasksInTrash, BoardNameTaken, BoardNotFound


def test_trash_lists_only_trashed_boards_most_recently_deleted_first(board_service):
    board_service.create_board("Still active")
    first = board_service.create_board("Deleted first")
    second = board_service.create_board("Deleted second")
    board_service.delete_board(first.id)
    board_service.delete_board(second.id)

    trashed = board_service.list_trash()

    assert [b.name for b in trashed] == ["Deleted second", "Deleted first"]
    assert all(b.deleted_at is not None for b in trashed)


def test_restore_board_makes_it_active_again(board_service):
    board = board_service.create_board("Onboarding")
    board_service.delete_board(board.id)

    restored = board_service.restore_board(board.id)

    assert restored.deleted_at is None
    assert [b.name for b in board_service.list_boards()] == ["Onboarding"]
    assert board_service.list_trash() == []


def test_restore_board_whose_name_is_now_taken_is_rejected(board_service):
    old = board_service.create_board("Onboarding")
    board_service.delete_board(old.id)
    board_service.create_board("ONBOARDING")

    with pytest.raises(BoardNameTaken, match="Rename it first"):
        board_service.restore_board(old.id)


def test_restore_board_that_is_not_in_trash_is_rejected(board_service):
    active = board_service.create_board("Onboarding")

    with pytest.raises(BoardNotFound):
        board_service.restore_board(active.id)
    with pytest.raises(BoardNotFound):
        board_service.restore_board(999999)


def test_delete_board_permanently_removes_the_row(board_service, session):
    board = board_service.create_board("Onboarding")
    board_service.delete_board(board.id)

    board_service.delete_board_permanently(board.id)

    rows = session.execute(
        text("SELECT count(*) FROM boards WHERE id = :id"), {"id": board.id}
    ).scalar_one()
    assert rows == 0


def test_delete_board_permanently_is_rejected_while_it_has_tasks_in_trash(
    board_service, task_service
):
    board = board_service.create_board("Onboarding")
    task = task_service.create_task(board.id, "Set up laptop")
    task_service.delete_task(task.id)
    board_service.delete_board(board.id)

    with pytest.raises(BoardHasTasksInTrash, match="1 task in trash"):
        board_service.delete_board_permanently(board.id)


def test_delete_board_permanently_is_rejected_for_an_active_board(board_service):
    active = board_service.create_board("Onboarding")

    with pytest.raises(BoardNotFound):
        board_service.delete_board_permanently(active.id)
    assert [b.name for b in board_service.list_boards()] == ["Onboarding"]
