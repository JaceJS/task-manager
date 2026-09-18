from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core.schemas import ApiResponse
from app.modules.boards.repository import BoardRepository
from app.modules.boards.schemas import BoardCreate, BoardInTrashOut, BoardOut, BoardRename
from app.modules.boards.service import BoardService
from app.modules.tasks.repository import TaskRepository

router = APIRouter(prefix="/api/boards", tags=["boards"])
trash_router = APIRouter(prefix="/api/trash/boards", tags=["trash"])


def get_board_service(session: Annotated[Session, Depends(get_session)]) -> BoardService:
    return BoardService(session, BoardRepository(session), TaskRepository(session))


BoardServiceDep = Annotated[BoardService, Depends(get_board_service)]


@router.get("", response_model=ApiResponse[list[BoardOut]])
def list_boards(service: BoardServiceDep) -> ApiResponse[list[BoardOut]]:
    boards = service.list_boards()
    return ApiResponse(message="Boards retrieved", data=boards)


@router.post("", response_model=ApiResponse[BoardOut], status_code=status.HTTP_201_CREATED)
def create_board(payload: BoardCreate, service: BoardServiceDep) -> ApiResponse[BoardOut]:
    board = service.create_board(payload.name)
    return ApiResponse(message="Board created", data=board)


@router.patch("/{board_id}", response_model=ApiResponse[BoardOut])
def rename_board(
    board_id: int, payload: BoardRename, service: BoardServiceDep
) -> ApiResponse[BoardOut]:
    board = service.rename_board(board_id, payload.name)
    return ApiResponse(message="Board renamed", data=board)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(board_id: int, service: BoardServiceDep) -> Response:
    service.delete_board(board_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{board_id}/restore", response_model=ApiResponse[BoardOut])
def restore_board(board_id: int, service: BoardServiceDep) -> ApiResponse[BoardOut]:
    board = service.restore_board(board_id)
    return ApiResponse(message="Board restored", data=board)


@trash_router.get("", response_model=ApiResponse[list[BoardInTrashOut]])
def list_boards_in_trash(service: BoardServiceDep) -> ApiResponse[list[BoardInTrashOut]]:
    boards = service.list_trash()
    return ApiResponse(message="Boards in trash retrieved", data=boards)


@trash_router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board_permanently(board_id: int, service: BoardServiceDep) -> Response:
    service.delete_board_permanently(board_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
