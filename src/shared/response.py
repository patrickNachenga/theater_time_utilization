import strawberry
from typing import Generic, TypeVar, List

T = TypeVar("T")


@strawberry.type
class Response(Generic[T]):
    status: bool
    code: int
    message: str
    data: T
