from datetime import datetime
from typing import Optional

import strawberry


@strawberry.input(description="Examcat Groups Input")
class ExamCatGroupsInput:
    uid: Optional[str] = None
    id: int
    name: str


@strawberry.type(description="Exam category Groups Node")
class ExamCatGroupsNode:
    id: int
    name: str


@strawberry.input(description="Exam Category Input")
class ExamCatsInput:
    uid: Optional[str] = None
    id: int
    name: str
    code: str
    exam_group_id: int


@strawberry.type(description="Exam Category Node")
class ExamCatsNode:
    id: int
    name: str
    code: str
    exam_group_id: int


@strawberry.input(description="Exam cat Groups Input")
class ExamResultsInput:
    uid: Optional[str] = None
    id: int
    student_id: int
    program_course_id: int
    exam_cat_id: int
    assess_no: int
    score: float
    out_of: float
    weight: int
    status: int
    publish: int


@strawberry.type(description="Exam cat Groups Node")
class ExamResultsNode:
    id: int
    student_id: int
    program_course_id: int
    exam_cat_id: int
    assess_no: int
    score: float
    out_of: float
    weight: int
    status: int
    publish: int


@strawberry.input(description="Exam cat Groups Input")
class ExamSummaryInput:
    uid: Optional[str] = None
    id: int
    student_id: int
    program_course_id: int
    marks: float
    gp: float
    grade: str
    remarks: str
    status: int


@strawberry.type(description="Exam Summary Node")
class ExamSummaryNode:
    id: int
    student_id: int
    program_course_id: int
    marks: float
    gp: float
    grade: str
    remarks: str
    status: int


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
    uid: Optional[str] = None
    code: str
    description: Optional[str] = None
    name: str
    short_name: Optional[str] = None
    offered: Optional[int] = 1
    department_uid: str


@strawberry.type(description="Course")
class CourseNode:
    id: int
    uid: str
    code: str
    description: str
    name: str
    short_name: str
    offered: int
    department_uid: str


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
