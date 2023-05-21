from typing import Optional

import strawberry


@strawberry.input(description="Student Input")
class StudentInput:
    uid: Optional[str] = None
    reg_no: str


@strawberry.type(description="Student")
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

@strawberry.input(description="Staff Input")
class GroupInput:
    uid: Optional[str] = None
    name: str
    code: str


@strawberry.type(description="Staff")
class GroupNode:
    id: int
    uid: str
    name: str
    code: str


@strawberry.input(description="Program Category Input")
class ProgramCategoryInput:
    uid: Optional[str] = None
    name: str


@strawberry.type(description="Program Category")
class ProgramCategoryNode:
    id: int
    uid: str
    name: str


@strawberry.input(description="Programme Input")
class ProgrammeInput:
    uid: Optional[str] = None
    programme_number: int
    code: int
    name: str
    short_name: str
    tcu_code: Optional[str] = None
    duration: Optional[int] = 0
    qualification: Optional[int] = 0
    max_student: Optional[int] = 0
    action: Optional[int] = 0
    # list of keys/relational attribute
    created_by: Optional[int] = 0
    programme_type_id: Optional[int] = 0
    specialization_area_id: Optional[int] = 0
    institute_unit_id: Optional[int] = 0


@strawberry.type(description="Programme outputs")
class ProgrammeNode:
    id: int
    uid: str
    programme_number: int
    code: int
    name: str
    short_name: str
    tcu_code: str
    duration: int
    qualification: str
    max_student: int
    action: int
    created_by: int
    programme_type_id: int
    specialization_area_id: int
    institute_unit_id: int


@strawberry.input(description="Course Input")
class CourseInput:
    id: Optional[str] = None
    code: str


@strawberry.type(description="Course")
class CourseNode:
    id: int
    uid: str
    code: str


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
