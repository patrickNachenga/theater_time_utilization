from enum import Enum
from typing import Optional

import strawberry
from pydantic import BaseModel


class ProgramCodeInput(BaseModel):
    code: Optional[str]
    uid: Optional[str]


@strawberry.enum
class Gender(str, Enum):
    Male = 'Male'
    Female = "Female"


@strawberry.input(description="Pagination Input")
class PaginationInput:
    offset: int = 0
    limit: int = 10
    search: Optional[str] = None


@strawberry.type(description="User Token")
class TokenNode:
    access_token: str
    refresh_token: str
    token_type: str


@strawberry.type
class LoginSuccess:
    status: bool
    access_token: str
    refresh_token: str
    token_type: str


@strawberry.type
class LoginError:
    status: bool
    message: str | None = None


