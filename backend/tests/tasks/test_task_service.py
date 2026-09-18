import pytest

from app.core.exceptions import ValidationFailed
from app.modules.boards.exceptions import BoardNotFound
from app.modules.tasks.exceptions import TaskNotFound
from app.modules.tasks.models import TaskStatus


@pytest.fixture
def board(board_service):
    return board_service.create_board("Onboarding")


def test_create_task_defaults_to_todo_and_trims_input(task_service, board):
    task = task_service.create_task(board.id, "  Set up laptop  ", "   ")

    assert task.id is not None
    assert task.board_id == board.id
    assert task.title == "Set up laptop"
    assert task.description is None
    assert task.status == TaskStatus.TODO
    assert task.created_at is not None


def test_create_task_rejects_empty_title(task_service, board):
    with pytest.raises(ValidationFailed, match="must not be empty"):
        task_service.create_task(board.id, "")


def test_create_task_rejects_whitespace_only_title(task_service, board):
    with pytest.raises(ValidationFailed, match="must not be empty"):
        task_service.create_task(board.id, "   ")


def test_create_task_rejects_title_longer_than_255(task_service, board):
    with pytest.raises(ValidationFailed, match="at most 255"):
        task_service.create_task(board.id, "x" * 256)


def test_create_task_on_board_that_does_not_exist_is_rejected(task_service):
    with pytest.raises(BoardNotFound):
        task_service.create_task(999999, "Set up laptop")


def test_list_tasks_returns_only_that_board_newest_first(task_service, board_service, board):
    other_board = board_service.create_board("Other")
    task_service.create_task(other_board.id, "Not mine")
    first = task_service.create_task(board.id, "First")
    second = task_service.create_task(board.id, "Second")

    titles = [task.title for task in task_service.list_tasks(board.id)]

    assert titles == ["Second", "First"]
    assert {first.board_id, second.board_id} == {board.id}


def test_list_tasks_can_filter_by_status(task_service, board):
    todo = task_service.create_task(board.id, "Still open")
    done = task_service.create_task(board.id, "Finished")
    task_service.update_task(done.id, status="DONE")

    done_tasks = task_service.list_tasks(board.id, status="DONE")
    todo_tasks = task_service.list_tasks(board.id, status="TODO")

    assert [task.id for task in done_tasks] == [done.id]
    assert [task.id for task in todo_tasks] == [todo.id]


def test_list_tasks_rejects_invalid_status(task_service, board):
    with pytest.raises(ValidationFailed, match="Status must be one of"):
        task_service.list_tasks(board.id, status="DOING")


def test_list_tasks_on_empty_board_returns_empty_list(task_service, board):
    assert task_service.list_tasks(board.id) == []


def test_list_tasks_of_board_that_does_not_exist_is_rejected(task_service):
    with pytest.raises(BoardNotFound):
        task_service.list_tasks(999999)


def test_update_status_changes_status_and_updated_at(task_service, board):
    task = task_service.create_task(board.id, "Set up laptop")
    created_updated_at = task.updated_at

    updated = task_service.update_task(task.id, status="IN_PROGRESS")

    assert updated.status == TaskStatus.IN_PROGRESS
    assert updated.updated_at > created_updated_at


def test_update_rejects_invalid_status(task_service, board):
    task = task_service.create_task(board.id, "Set up laptop")

    with pytest.raises(ValidationFailed, match="Status must be one of"):
        task_service.update_task(task.id, status="ARCHIVED")

    assert task_service.get_task(task.id).status == TaskStatus.TODO


def test_update_task_that_does_not_exist_is_rejected(task_service):
    with pytest.raises(TaskNotFound):
        task_service.update_task(999999, status="DONE")


def test_update_rejects_blank_title(task_service, board):
    task = task_service.create_task(board.id, "Set up laptop")

    with pytest.raises(ValidationFailed, match="must not be empty"):
        task_service.update_task(task.id, title="   ")

    assert task_service.get_task(task.id).title == "Set up laptop"


def test_update_without_any_field_is_rejected(task_service, board):
    task = task_service.create_task(board.id, "Set up laptop")

    with pytest.raises(ValidationFailed, match="at least one field"):
        task_service.update_task(task.id)


def test_delete_task_moves_it_to_trash(task_service, board):
    task = task_service.create_task(board.id, "Set up laptop")

    task_service.delete_task(task.id)

    assert task.deleted_at is not None
    assert task_service.list_tasks(board.id) == []


def test_delete_task_that_does_not_exist_is_rejected(task_service):
    with pytest.raises(TaskNotFound):
        task_service.delete_task(999999)


def test_task_in_trash_can_no_longer_be_updated_or_deleted(task_service, board):
    task = task_service.create_task(board.id, "Set up laptop")
    task_service.delete_task(task.id)

    with pytest.raises(TaskNotFound):
        task_service.update_task(task.id, status="DONE")
    with pytest.raises(TaskNotFound):
        task_service.delete_task(task.id)
