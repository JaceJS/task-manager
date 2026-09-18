from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import (
    FOREIGN_KEY_VIOLATION,
    RESTRICT_VIOLATION,
    UNIQUE_VIOLATION,
    sqlstate_of,
)
from app.core.validation import clean_required_text
from app.modules.boards.exceptions import (
    BoardHasActiveTasks,
    BoardHasTasksInTrash,
    BoardNameTaken,
    BoardNotFound,
)
from app.modules.boards.models import Board
from app.modules.boards.repository import BoardRepository
from app.modules.tasks.repository import TaskRepository


class BoardService:
    def __init__(
        self, session: Session, boards: BoardRepository, tasks: TaskRepository
    ) -> None:
        self.session = session
        self.boards = boards
        self.tasks = tasks

    def list_boards(self) -> list[Board]:
        return self.boards.list_active()

    def get_board(self, board_id: int) -> Board:
        board = self.boards.get_active(board_id)
        if board is None:
            raise BoardNotFound(board_id)
        return board

    def create_board(self, name: str | None) -> Board:
        clean_name = clean_required_text(name, "Name")
        if self.boards.find_active_by_name(clean_name) is not None:
            raise BoardNameTaken(clean_name)

        board = Board(name=clean_name)
        self.boards.add(board)
        self._commit_name(clean_name)
        return board

    def rename_board(self, board_id: int, name: str | None) -> Board:
        board = self.get_board(board_id)
        clean_name = clean_required_text(name, "Name")
        holder = self.boards.find_active_by_name(clean_name)
        if holder is not None and holder.id != board.id:
            raise BoardNameTaken(clean_name)

        board.name = clean_name
        self._commit_name(clean_name)
        self.session.refresh(board)
        return board

    def delete_board(self, board_id: int) -> None:
        board = self.get_board(board_id)

        active_tasks = self.tasks.count_active_by_board(board_id)
        if active_tasks > 0:
            raise BoardHasActiveTasks(active_tasks)

        board.deleted_at = func.clock_timestamp()
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            if sqlstate_of(error) == RESTRICT_VIOLATION:
                raise BoardHasActiveTasks(self.tasks.count_active_by_board(board_id)) from error
            raise
        self.session.refresh(board)

    def list_trash(self) -> list[Board]:
        return self.boards.list_trashed()

    def restore_board(self, board_id: int) -> Board:
        board = self.boards.get_trashed(board_id)
        if board is None:
            raise BoardNotFound(board_id, in_trash=True)
        hint = "Rename it first."
        if self.boards.find_active_by_name(board.name) is not None:
            raise BoardNameTaken(board.name, hint)

        board.deleted_at = None
        self._commit_name(board.name, hint)
        self.session.refresh(board)
        return board

    def delete_board_permanently(self, board_id: int) -> None:
        board = self.boards.get_trashed(board_id)
        if board is None:
            raise BoardNotFound(board_id, in_trash=True)
        task_rows = self.tasks.count_all_by_board(board_id)
        if task_rows > 0:
            raise BoardHasTasksInTrash(task_rows)

        self.boards.delete(board)
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            if sqlstate_of(error) == FOREIGN_KEY_VIOLATION:
                raise BoardHasTasksInTrash(self.tasks.count_all_by_board(board_id)) from error
            raise

    def _commit_name(self, name: str, hint: str = "") -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            if sqlstate_of(error) == UNIQUE_VIOLATION:
                raise BoardNameTaken(name, hint) from error
            raise
