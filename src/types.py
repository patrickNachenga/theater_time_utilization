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


@strawberry.type(description="Staff")
class GroupNode:
    id: int
    uid: str
    name: str
    code: str


@strawberry.input(description="Course Input")
class CourseInput:
    uid: Optional[str] = None
    code: str
    description: Optional[str] = None
    name: str
    offered: Optional[int] = 1
    department_id: int


@strawberry.type(description="Course")
class CourseNode:
    id: int
    uid: str
    code: str
    description: str
    name: str
    offered: int
    department_id: int


@strawberry.type(description="Program Category")
class ProgramCategoryNode:
    id: int
    uid: str
    name: str
    short_name: str
    created_by: int
    created_at: datetime
    updated_at: datetime


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
    program_category: ProgramCategoryNode
    department_id: int
    campus_id: int
    created_by: str
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Program Semester Input")
class ProgramSemesterInput:
    uid: Optional[str] = None
    program_id: int
    academic_year_id: int
    study_year: int
    semester: int
    core_credits: float
    elective_credits: float
    created_by: Optional[str] = None


@strawberry.type(description="Program Semester output")
class ProgramSemesterNode:
    id: int
    uid: str
    program_id: int
    program: ProgramNode
    academic_year_id: int
    study_year: int
    semester: int
    core_credits: float
    elective_credits: float
    created_by: str
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Course Category Input")
class CourseCategoryInput:
    uid: Optional[str] = None
    name: str
    description: Optional[str] = None


@strawberry.type(description="Course Category")
class CourseCategoryNode:
    id: int
    uid: str
    description: str
    name: str

    created_by: int
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Program Course Input")
class ProgramCourseInput:
    uid: Optional[str] = None
    program_semester_id: int
    course_id: int
    course_category_id: int
    credit: Optional[float] = 0.0
    lecture_hours: Optional[float] = 0.0
    seminar_hours: Optional[float] = 0.0
    practical_hours: Optional[float] = 0.0
    assignment_hours: Optional[float] = 0.0
    independent_study_hours: Optional[float] = 0
    pass_hours: Optional[float] = 0.0


@strawberry.type(description="Program Course outputs")
class ProgramCourseNode:
    id: int
    uid: str
    program_semester_id: int
    program_semester: ProgramSemesterNode
    course_id: int
    course: CourseNode
    course_category_id: int
    course_category: CourseCategoryNode
    credit: float
    lecture_hours: float
    seminar_hours: float
    practical_hours: float
    assignment_hours: float
    independent_study_hours: float
    pass_hours: float

    created_by: int
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Program Category Input")
class ProgramCategoryInput:
    uid: Optional[str] = None
    name: str
    short_name: Optional[str] = None


@strawberry.input(description="Course Learn Outcome Input")
class CourseLearnOutcomeInput:
    uid: Optional[str] = None
    staff_id: str
    program_course_id: str
    learning_outcome: str


@strawberry.type(description="Course Learn outcome")
class CourseLearnOutcomeNode:
    id: int
    uid: str
    staff_id: str
    program_course_id: str
    learning_outcome: str
    created_by: str
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Academic Year Input")
class AcademicYearInput:
    uid: Optional[str] = None
    id: int
    name: str
    status: Optional[int] = 1
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@strawberry.type(description="Academic Year")
class AcademicYearNode:
    id: int
    uid: str
    name: str
    status: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]


@strawberry.type(description="Course Assessment")
class CourseAssessmentNode:
    id: int
    uid: str
    program_course_id: int
    exam_category_id: int
    minimum_exams: int
    can_exceed_minimum: Optional[int] = 0
    maximum_score: int


@strawberry.input(description="Course Assessment Input")
class CourseAssessmentInput:
    uid: Optional[str] = None
    id: int
    program_course_id: int
    exam_category_id: int
    minimum_exams: int
    can_exceed_minimum: Optional[int] = 0
    maximum_score: int


@strawberry.input(description="Course Allocation Input")
class CourseAllocationInput:
    uid: Optional[str] = None
    program_course_id: str
    staff_id: Optional[str] = None


@strawberry.type(description="Course Allocation")
class CourseAllocationNode:
    id: int
    uid: str
    program_course_id: str
    staff_id: str


@strawberry.type(description="Program Course Assessment Input")
class ProgramCourseAssessmentNode:
    id: int
    uid: str
    program_course_id: int
    exam_category_id: int
    minimum_exams: int
    can_exceed_minimum_by: Optional[int] = 0
    maximum_score: int


@strawberry.input(description="Course Assessment Input")
class ProgramCourseAssessmentInput:
    uid: Optional[str] = None
    id: int
    program_course_id: int
    exam_category_id: int
    minimum_exams: int
    can_exceed_minimum_by: Optional[int] = 0
    maximum_score: int


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


@strawberry.input
class Pagination:
    page: int
    limit: int
    search: Optional[str] = None


LoginResult = strawberry.union("LoginResult", types=(LoginSuccess, LoginError))
