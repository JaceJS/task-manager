from app.core.exceptions import DomainError


class TaskNotFound(DomainError):
    def __init__(self, task_id: int, in_trash: bool = False) -> None:
        where = " in trash" if in_trash else ""
        super().__init__(f"Task {task_id} was not found{where}")


class BoardInTrash(DomainError):
    def __init__(self, board_id: int, board_name: str | None = None) -> None:
        if board_name is None:
            super().__init__(f"Board {board_id} is in trash")
        else:
            super().__init__(f"Restore the board '{board_name}' first")
