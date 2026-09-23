from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class Page(BaseModel, Generic[T]):
    items: list[T]
    pagination: Pagination


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    code: str
    request_id: str | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)