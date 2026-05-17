from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class MessageResponse(BaseModel):
    success: bool
    message: str

class DataResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T