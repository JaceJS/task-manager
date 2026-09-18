import pytest

from app.core.exceptions import ValidationFailed
from app.modules.boards.exceptions import BoardNameTaken, BoardNotFound


def test_rename_board_changes_name_and_updated_at(board_service):
    board = board_service.create_board("Onboarding")
    before = board.updated_at

    renamed = board_service.rename_board(board.id, "  Client onboarding  ")

    assert renamed.name == "Client onboarding"
    assert renamed.updated_at > before
    assert [b.name for b in board_service.list_boards()] == ["Client onboarding"]


@pytest.mark.parametrize("name", ["", "   "])
def test_rename_board_rejects_blank_name(board_service, name):
    board = board_service.create_board("Onboarding")

    with pytest.raises(ValidationFailed, match="must not be empty"):
        board_service.rename_board(board.id, name)


def test_rename_board_rejects_name_of_another_active_board(board_service):
    board_service.create_board("Onboarding")
    other = board_service.create_board("Q4 Campaign")

    with pytest.raises(BoardNameTaken):
        board_service.rename_board(other.id, "ONBOARDING")


def test_rename_board_that_does_not_exist_or_is_in_trash_is_rejected(board_service):
    trashed = board_service.create_board("Old board")
    board_service.delete_board(trashed.id)

    with pytest.raises(BoardNotFound):
        board_service.rename_board(999999, "Anything")
    with pytest.raises(BoardNotFound):
        board_service.rename_board(trashed.id, "Anything")


def test_rename_board_may_change_only_the_case_of_its_own_name(board_service):
    board = board_service.create_board("onboarding")

    renamed = board_service.rename_board(board.id, "Onboarding")

    assert renamed.name == "Onboarding"
