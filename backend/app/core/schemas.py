from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="forbid",
    )


class ApiResponse(BaseModel, Generic[T]):
    message: str
    data: T | None = None


def error_body(message: str) -> dict[str, None | str]:
    return {"message": message, "data": None}
