"""Common Pydantic schemas."""
from pydantic import BaseModel
from typing import TypeVar, Generic, List, Optional
T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    per_page: int
    items: List[T]  # type: ignore[misc]

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
