from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core.schemas import ApiResponse
from app.modules.boards.repository import BoardRepository
from app.modules.tasks.models import TaskStatus
from app.modules.tasks.repository import TaskRepository
from app.modules.tasks.schemas import TaskCreate, TaskInTrashOut, TaskOut, TaskUpdate
from app.modules.tasks.service import TaskService

router = APIRouter(prefix="/api", tags=["tasks"])
trash_router = APIRouter(prefix="/api/trash/tasks", tags=["trash"])


def get_task_service(session: Annotated[Session, Depends(get_session)]) -> TaskService:
    return TaskService(session, TaskRepository(session), BoardRepository(session))


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


@router.get("/boards/{board_id}/tasks", response_model=ApiResponse[list[TaskOut]])
def list_tasks(
    board_id: int,
    service: TaskServiceDep,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
) -> ApiResponse[list[TaskOut]]:
    tasks = service.list_tasks(board_id, status_filter)
    return ApiResponse(message="Tasks retrieved", data=tasks)


@router.post(
    "/boards/{board_id}/tasks",
    response_model=ApiResponse[TaskOut],
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    board_id: int, payload: TaskCreate, service: TaskServiceDep
) -> ApiResponse[TaskOut]:
    task = service.create_task(board_id, payload.title, payload.description)
    return ApiResponse(message="Task created", data=task)


@router.patch("/tasks/{task_id}", response_model=ApiResponse[TaskOut])
def update_task(
    task_id: int, payload: TaskUpdate, service: TaskServiceDep
) -> ApiResponse[TaskOut]:
    changes = payload.model_dump(exclude_unset=True)
    task = service.update_task(task_id, **changes)
    return ApiResponse(message="Task updated", data=task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskServiceDep) -> Response:
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/tasks/{task_id}/restore", response_model=ApiResponse[TaskOut])
def restore_task(task_id: int, service: TaskServiceDep) -> ApiResponse[TaskOut]:
    task = service.restore_task(task_id)
    return ApiResponse(message="Task restored", data=task)


@trash_router.get("", response_model=ApiResponse[list[TaskInTrashOut]])
def list_tasks_in_trash(service: TaskServiceDep) -> ApiResponse[list[TaskInTrashOut]]:
    tasks = service.list_trash()
    return ApiResponse(message="Tasks in trash retrieved", data=tasks)


@trash_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_permanently(task_id: int, service: TaskServiceDep) -> Response:
    service.delete_task_permanently(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
