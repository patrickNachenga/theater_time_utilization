from typing import Optional

import strawberry


@strawberry.input(description="Student Input")
class StudentInput:
    uid: Optional[str] = None
    reg_no: str


@strawberry.type(description="User")
class StudentNode:
    id: int
    uid: str
    reg_no: str


@strawberry.input(description="Staff Input")
class StaffInput:
    uid: Optional[str] = None
    pf_number: str


@strawberry.type(description="Staff")
class StaffNode:
    id: int
    uid: str
    pf_number: str


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


LoginResult = strawberry.union("LoginResult", types=(LoginSuccess, LoginError))
