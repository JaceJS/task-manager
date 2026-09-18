from app.core.exceptions import DomainError


class BoardNotFound(DomainError):
    def __init__(self, board_id: int, in_trash: bool = False) -> None:
        where = " in trash" if in_trash else ""
        super().__init__(f"Board {board_id} was not found{where}")


class BoardNameTaken(DomainError):
    def __init__(self, name: str, hint: str = "") -> None:
        message = f"A board named '{name}' already exists"
        super().__init__(f"{message}. {hint}" if hint else message)


class BoardHasActiveTasks(DomainError):
    def __init__(self, task_count: int) -> None:
        tasks, them = ("task", "it") if task_count == 1 else ("tasks", "them")
        super().__init__(f"Board still has {task_count} {tasks}. Delete {them} first.")


class BoardHasTasksInTrash(DomainError):
    def __init__(self, task_count: int) -> None:
        tasks, them = ("task", "it") if task_count == 1 else ("tasks", "them")
        super().__init__(
            f"Board still has {task_count} {tasks} in trash. Delete {them} permanently first."
        )
