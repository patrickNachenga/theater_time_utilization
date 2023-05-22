from datetime import datetime
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


int


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


@strawberry.input(description="Program Input")
class ProgramInput:
    uid: Optional[str] = None
    code: str
    tcu_code: Optional[str] = None
    nacte_code: Optional[str] = None
    name: str
    short_name: str
    duration: Optional[int] = 0
    reg_code: Optional[str] = None
    program_category_id: Optional[int] = 0
    department_id: Optional[int] = 0
    campus_id: Optional[int] = 0


@strawberry.type(description="Program outputs")
class ProgramNode:
    id: int
    uid: str
    code: str
    name: str
    short_name: str
    tcu_code: str
    nacte_code: str
    duration: int
    reg_code: str
    program_category_id: int
    department_id: int
    campus_id: int


@strawberry.input(description="program_sem_unit Input")
class ProgramSemester:
    uid: Optional[str] = None
    program_code: str
    ac_year: int
    study_year: int
    semester: Optional[int] = 0
    core_cwt: Optional[float] = 0
    opt_cwt: Optional[float] = 0
    created_by: str


@strawberry.type(description="program_sem_unit output")
class ProgramSemesterNode:
    id: str
    uid: str
    program_code: str
    ac_year: int
    study_year: int
    semester: int
    core_cwt: int
    opt_cwt: int
    created_by: str
    created_at: datetime
    updated_at: datetime


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
