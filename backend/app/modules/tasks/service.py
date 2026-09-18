from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import RESTRICT_VIOLATION, sqlstate_of
from app.core.exceptions import ValidationFailed
from app.core.validation import clean_optional_text, clean_required_text
from app.modules.boards.repository import BoardRepository
from app.modules.boards.exceptions import BoardNotFound
from app.modules.tasks.exceptions import BoardInTrash, TaskNotFound
from app.modules.tasks.models import Task, TaskStatus
from app.modules.tasks.repository import TaskRepository

UNSET: Final[Any] = object()


@dataclass(frozen=True)
class TrashedTask:
    id: int
    board_id: int
    board_name: str
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime


class TaskService:
    def __init__(
        self, session: Session, tasks: TaskRepository, boards: BoardRepository
    ) -> None:
        self.session = session
        self.tasks = tasks
        self.boards = boards

    def list_tasks(self, board_id: int, status: str | None = None) -> list[Task]:
        self._require_board(board_id)
        if status is not None:
            status = self._validate_status(status)
        return self.tasks.list_active_by_board(board_id, status)

    def create_task(
        self, board_id: int, title: str | None, description: str | None = None
    ) -> Task:
        self._require_board(board_id)
        task = Task(
            board_id=board_id,
            title=clean_required_text(title, "Title"),
            description=clean_optional_text(description),
            status=TaskStatus.TODO,
        )
        self.tasks.add(task)
        self._commit(board_id)
        return task

    def update_task(
        self,
        task_id: int,
        status: Any = UNSET,
        title: Any = UNSET,
        description: Any = UNSET,
    ) -> Task:
        if status is UNSET and title is UNSET and description is UNSET:
            raise ValidationFailed("Provide at least one field to update")

        task = self.get_task(task_id)
        if status is not UNSET:
            task.status = self._validate_status(status)
        if title is not UNSET:
            task.title = clean_required_text(title, "Title")
        if description is not UNSET:
            task.description = clean_optional_text(description)

        self._commit(task.board_id)
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        task.deleted_at = func.clock_timestamp()
        self._commit(task.board_id)
        self.session.refresh(task)

    def list_trash(self) -> list[TrashedTask]:
        return [
            TrashedTask(
                id=task.id,
                board_id=task.board_id,
                board_name=board_name,
                title=task.title,
                description=task.description,
                status=task.status,
                created_at=task.created_at,
                updated_at=task.updated_at,
                deleted_at=task.deleted_at,
            )
            for task, board_name in self.tasks.list_trashed_with_board_name()
        ]

    def restore_task(self, task_id: int) -> Task:
        task = self.tasks.get_trashed(task_id)
        if task is None:
            raise TaskNotFound(task_id, in_trash=True)
        trashed_board = self.boards.get_trashed(task.board_id)
        if trashed_board is not None:
            raise BoardInTrash(trashed_board.id, trashed_board.name)

        task.deleted_at = None
        self._commit(task.board_id)
        self.session.refresh(task)
        return task

    def delete_task_permanently(self, task_id: int) -> None:
        task = self.tasks.get_trashed(task_id)
        if task is None:
            raise TaskNotFound(task_id, in_trash=True)
        self.tasks.delete(task)
        self.session.commit()

    def get_task(self, task_id: int) -> Task:
        task = self.tasks.get_active(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def _require_board(self, board_id: int) -> None:
        if self.boards.get_active(board_id) is None:
            raise BoardNotFound(board_id)

    def _validate_status(self, status: Any) -> str:
        try:
            return TaskStatus(status).value
        except ValueError as error:
            allowed = ", ".join(s.value for s in TaskStatus)
            raise ValidationFailed(f"Status must be one of: {allowed}") from error

    def _commit(self, board_id: int) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            if sqlstate_of(error) == RESTRICT_VIOLATION:
                raise BoardInTrash(board_id) from error
            raise
