from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.boards.models import Board
from app.modules.tasks.models import Task


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active_by_board(self, board_id: int, status: str | None = None) -> list[Task]:
        stmt = select(Task).where(Task.board_id == board_id, Task.deleted_at.is_(None))
        if status is not None:
            stmt = stmt.where(Task.status == status)
        stmt = stmt.order_by(Task.created_at.desc(), Task.id.desc())
        return list(self.session.scalars(stmt))

    def get_active(self, task_id: int) -> Task | None:
        stmt = select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        return self.session.scalars(stmt).one_or_none()

    def count_active_by_board(self, board_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Task)
            .where(Task.board_id == board_id, Task.deleted_at.is_(None))
        )
        return self.session.scalar(stmt) or 0

    def count_all_by_board(self, board_id: int) -> int:
        stmt = select(func.count()).select_from(Task).where(Task.board_id == board_id)
        return self.session.scalar(stmt) or 0

    def list_trashed_with_board_name(self) -> list[tuple[Task, str]]:
        stmt = (
            select(Task, Board.name)
            .join(Board, Board.id == Task.board_id)
            .where(Task.deleted_at.is_not(None))
            .order_by(Task.deleted_at.desc(), Task.id.desc())
        )
        return [(task, board_name) for task, board_name in self.session.execute(stmt)]

    def get_trashed(self, task_id: int) -> Task | None:
        stmt = select(Task).where(Task.id == task_id, Task.deleted_at.is_not(None))
        return self.session.scalars(stmt).one_or_none()

    def add(self, task: Task) -> None:
        self.session.add(task)

    def delete(self, task: Task) -> None:
        self.session.delete(task)
