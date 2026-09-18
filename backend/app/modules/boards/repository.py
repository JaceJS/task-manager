from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.boards.models import Board


class BoardRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(self) -> list[Board]:
        stmt = (
            select(Board)
            .where(Board.deleted_at.is_(None))
            .order_by(Board.created_at.desc(), Board.id.desc())
        )
        return list(self.session.scalars(stmt))

    def get_active(self, board_id: int) -> Board | None:
        stmt = select(Board).where(Board.id == board_id, Board.deleted_at.is_(None))
        return self.session.scalars(stmt).one_or_none()

    def find_active_by_name(self, name: str) -> Board | None:
        stmt = select(Board).where(
            func.lower(Board.name) == name.lower(), Board.deleted_at.is_(None)
        )
        return self.session.scalars(stmt).one_or_none()

    def list_trashed(self) -> list[Board]:
        stmt = (
            select(Board)
            .where(Board.deleted_at.is_not(None))
            .order_by(Board.deleted_at.desc(), Board.id.desc())
        )
        return list(self.session.scalars(stmt))

    def get_trashed(self, board_id: int) -> Board | None:
        stmt = select(Board).where(Board.id == board_id, Board.deleted_at.is_not(None))
        return self.session.scalars(stmt).one_or_none()

    def add(self, board: Board) -> None:
        self.session.add(board)

    def delete(self, board: Board) -> None:
        self.session.delete(board)
