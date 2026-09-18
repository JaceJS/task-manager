from datetime import datetime

from app.core.schemas import CamelModel


class BoardCreate(CamelModel):
    name: str


class BoardRename(CamelModel):
    name: str


class BoardOut(CamelModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class BoardInTrashOut(BoardOut):
    deleted_at: datetime
