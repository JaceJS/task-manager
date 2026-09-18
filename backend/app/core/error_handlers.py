import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import DomainError, ValidationFailed
from app.core.schemas import error_body
from app.modules.boards.exceptions import (
    BoardHasActiveTasks,
    BoardHasTasksInTrash,
    BoardNameTaken,
    BoardNotFound,
)
from app.modules.tasks.exceptions import BoardInTrash, TaskNotFound

logger = logging.getLogger(__name__)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    ValidationFailed: 422,
    BoardNotFound: 404,
    TaskNotFound: 404,
    BoardNameTaken: 409,
    BoardHasActiveTasks: 409,
    BoardHasTasksInTrash: 409,
    BoardInTrash: 409,
}


def _status_for(error: DomainError) -> int:
    for error_type in type(error).__mro__:
        if error_type in STATUS_BY_ERROR:
            return STATUS_BY_ERROR[error_type]
    return 500


def _first_validation_message(error: RequestValidationError) -> str:
    first = error.errors()[0]
    location = [str(part) for part in first.get("loc", []) if part not in ("body", "query")]
    field = ".".join(location)
    message = first.get("msg", "Invalid value")
    return f"{field}: {message}" if field else message


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(status_code=_status_for(error), content=error_body(error.message))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, error: RequestValidationError
    ) -> JSONResponse:
        if any(item.get("type") == "json_invalid" for item in error.errors()):
            return JSONResponse(
                status_code=400, content=error_body("Request body is not valid JSON")
            )
        return JSONResponse(
            status_code=422, content=error_body(_first_validation_message(error))
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        _: Request, error: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content=error_body(str(error.detail)))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, error: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=error)
        return JSONResponse(
            status_code=500, content=error_body("Something went wrong on the server")
        )
