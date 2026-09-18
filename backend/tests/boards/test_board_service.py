import pytest
from sqlalchemy import text

from app.core.exceptions import ValidationFailed
from app.modules.boards.exceptions import BoardHasActiveTasks, BoardNameTaken, BoardNotFound


def test_create_board_trims_name_and_sets_timestamps(board_service):
    board = board_service.create_board("  Onboarding  ")

    assert board.id is not None
    assert board.name == "Onboarding"
    assert board.created_at is not None
    assert board.deleted_at is None


def test_create_board_rejects_empty_name(board_service):
    with pytest.raises(ValidationFailed, match="must not be empty"):
        board_service.create_board("")


def test_create_board_rejects_whitespace_only_name(board_service):
    with pytest.raises(ValidationFailed, match="must not be empty"):
        board_service.create_board("   ")


def test_create_board_rejects_name_longer_than_255(board_service):
    with pytest.raises(ValidationFailed, match="at most 255"):
        board_service.create_board("x" * 256)


def test_create_board_rejects_name_already_taken_ignoring_case(board_service):
    board_service.create_board("Onboarding")

    with pytest.raises(BoardNameTaken):
        board_service.create_board("  onboarding  ")


def test_list_boards_returns_active_boards_newest_first(board_service):
    first = board_service.create_board("First")
    second = board_service.create_board("Second")
    board_service.delete_board(first.id)

    names = [board.name for board in board_service.list_boards()]

    assert names == ["Second"]
    assert second.id == board_service.list_boards()[0].id


def test_delete_board_without_active_tasks_moves_it_to_trash(board_service):
    board = board_service.create_board("Onboarding")

    board_service.delete_board(board.id)

    assert board.deleted_at is not None
    assert board_service.list_boards() == []


def test_delete_board_with_active_tasks_is_rejected(board_service, task_service):
    board = board_service.create_board("Onboarding")
    task_service.create_task(board.id, "Set up laptop")

    with pytest.raises(BoardHasActiveTasks, match="still has 1 task"):
        board_service.delete_board(board.id)

    assert board_service.get_board(board.id).deleted_at is None
    assert len(task_service.list_tasks(board.id)) == 1


def test_delete_board_that_does_not_exist_is_rejected(board_service):
    with pytest.raises(BoardNotFound):
        board_service.delete_board(999999)


def test_delete_board_whose_tasks_are_all_in_trash_succeeds(board_service, task_service):
    board = board_service.create_board("Onboarding")
    task = task_service.create_task(board.id, "Set up laptop")
    task_service.delete_task(task.id)

    board_service.delete_board(board.id)

    assert board_service.list_boards() == []


def test_name_of_a_trashed_board_can_be_reused(board_service, session):
    first = board_service.create_board("Onboarding")
    board_service.delete_board(first.id)

    reused = board_service.create_board("Onboarding")

    assert reused.id != first.id
    still_there = session.execute(
        text("SELECT count(*) FROM boards WHERE lower(name) = 'onboarding'")
    ).scalar_one()
    assert still_there == 2
