from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.error_handlers import register_error_handlers
from app.modules.boards.router import router as boards_router
from app.modules.boards.router import trash_router as boards_trash_router
from app.modules.tasks.router import router as tasks_router
from app.modules.tasks.router import trash_router as tasks_trash_router

FRONTEND_ORIGIN = "http://localhost:5173"

app = FastAPI(title="Task Manager API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(boards_router)
app.include_router(tasks_router)
app.include_router(boards_trash_router)
app.include_router(tasks_trash_router)
