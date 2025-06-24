from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List, Optional

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    object: Optional[T] = None
    errors: Optional[List[str]] = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    object: List[T] = []
    page_number: int
    page_size: int
    total_size: int
    errors: Optional[List[str]] = None
