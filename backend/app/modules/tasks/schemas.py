from datetime import datetime

from app.core.schemas import CamelModel
from app.modules.tasks.models import TaskStatus


class TaskCreate(CamelModel):
    title: str
    description: str | None = None


class TaskUpdate(CamelModel):
    status: TaskStatus | None = None
    title: str | None = None
    description: str | None = None


class TaskOut(CamelModel):
    id: int
    board_id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskInTrashOut(TaskOut):
    board_name: str
    deleted_at: datetime
