import uuid
from datetime import datetime
from typing import Optional, List

import strawberry

@strawberry.input
class PaginationInput:
    offset: int = 0
    limit: int = 10
    search: Optional[str] = None

@strawberry.input(description="Academic Year Input")
class AcademicYearInput:
    uid: Optional[str] = None
    name: str
    status: Optional[int] = 1
    start_date: datetime
    end_date: datetime


@strawberry.type(description="Academic Year")
class AcademicYearNode:
    uid: str
    name: str
    status: Optional[int]
    start_date: str
    end_date: str
    created_at: datetime
    updated_at: datetime


@strawberry.type(description="AcademicYear Country")
class AcademicYearListNode:
    items: List[AcademicYearNode]
    total_count: int


@strawberry.input(description="Exam Category Groups Input")
class ExamCatGroupsInput:
    uid: Optional[str] = None
    id: int
    name: str


@strawberry.type(description="Exam category Groups Output")
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


@strawberry.type(description="Exam Category Output")
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


@strawberry.type(description="Exam Category Groups Output")
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


@strawberry.input(description="Exam Category Groups Input")
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


@strawberry.type(description="Exam Summary Output")
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


@strawberry.type(description="Student Output")
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


@strawberry.input(description="Group Input")
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
    department_uid: str


@strawberry.type(description="Course Output")
class CourseNode:
    id: int
    uid: str
    code: str
    description: str
    name: str
    offered: int
    department_uid: str


@strawberry.input(description="Program Category Input")
class ProgramCategoryInput:
    uid: Optional[str] = None
    name: str
    short_name: Optional[str] = None


@strawberry.type(description="Program Category Output")
class ProgramCategoryNode:
    uid: str
    name: str
    short_name: str
    created_by: str
    created_at: datetime
    updated_at: datetime


@strawberry.type(description="Program Category paginated Output")
class ProgramCategoryListNode:
    items: List[ProgramCategoryNode]
    total_count: int


@strawberry.input(description="Program Semester Input")
class ProgramSemesterInput:
    uid: Optional[str] = None
    program_uid: str
    academic_year_uid: str
    study_year: int
    semester: int
    core_credits: float
    elective_credits: float
    created_by: Optional[str] = None


@strawberry.type(description="Program Semester output")
class ProgramSemesterNode:
    id: int
    uid: str
    program_id: str
    academic_year_id: str
    study_year: int
    semester: int
    core_credits: float
    elective_credits: float
    created_by: str
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Course Learn Outcome Input")
class CourseLearnOutcomeInput:
    uid: Optional[str] = None
    staff_id: str
    program_course_id: str
    learning_outcome: str


@strawberry.type(description="Course Learn Outcome Output")
class CourseLearnOutcomeNode:
    id: int
    uid: str
    staff_id: str
    program_course_id: str
    learning_outcome: str
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
    registration_code: Optional[str] = None
    program_category_id: Optional[int] = 0
    department_uid: str


@strawberry.type(description="Program Output")
class ProgramNode:
    uid: str
    code: str
    name: str
    short_name: str
    tcu_code: str
    nacte_code: str
    duration: int
    registration_code: str
    program_category_id: int
    program_category: ProgramCategoryNode
    department_uid: str


@strawberry.type(description="Program paginated Output")
class ProgramListNode:
    items: List[ProgramNode]
    total_count: int


@strawberry.input(description="Program Semester Input")
class ProgramSemesterInput:
    uid: Optional[str] = None
    program_uid: str
    academic_year_uid: str
    study_year: int
    semester: int
    core_credits: float
    elective_credits: float


@strawberry.type(description="Program Semester output")
class ProgramSemesterNode:
    uid: str
    program: ProgramNode
    academic_year: AcademicYearNode
    study_year: int
    semester: int
    core_credits: float
    elective_credits: float
    created_at: datetime
    updated_at: datetime


@strawberry.type(description="Program Semester paginated Output")
class ProgramSemesterListNode:
    items: List[ProgramSemesterNode]
    total_count: int


@strawberry.input(description="Course Category Input")
class CourseCategoryInput:
    uid: Optional[str] = None
    name: str
    description: Optional[str] = None


@strawberry.type(description="Course Category Output")
class CourseCategoryNode:
    id: int
    uid: str
    description: str
    name: str


@strawberry.input(description="Program Course Input")
class ProgramCourseInput:
    uid: Optional[str] = None
    program_semester_uid: str
    course_uid: str
    course_category_uid: str
    credit: Optional[float] = 0.0
    lecture_hours: Optional[float] = 0.0
    seminar_hours: Optional[float] = 0.0
    practical_hours: Optional[float] = 0.0
    assignment_hours: Optional[float] = 0.0
    independent_study_hours: Optional[float] = 0
    pass_hours: Optional[float] = 0.0


@strawberry.type(description="Program Course outputs")
class ProgramCourseNode:
    uid: str
    program_semester: ProgramSemesterNode
    course: CourseNode
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


@strawberry.type(description="Program Course paginated Output")
class ProgramCourseListNode:
    items: List[ProgramSemesterNode]
    total_count: int



@strawberry.input(description="Course Learn Outcome Input")
class CourseLearnOutcomeInput:
    uid: Optional[str] = None
    staff_uid: str
    program_course_id: str
    learning_outcome: str


@strawberry.type(description="Course Learn outcome")
class CourseLearnOutcomeNode:
    id: int
    uid: str
    staff_uid: str
    program_course_id: str
    learning_outcome: str
    created_by: str
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Program Course Assessment Input")
class ProgramCourseAssessmentInput:
    uid: Optional[str] = None
    program_course_id: int
    exam_category_uid: str
    minimum_exams: int
    can_exceed_minimum: Optional[int] = 0
    maximum_score: int


@strawberry.type(description="Program Course Assessment Output")
class ProgramCourseAssessmentNode:
    id: int
    uid: str
    program_course_id: int
    program_course: ProgramCourseNode
    exam_category_uid: str
    minimum_exams: int
    can_exceed_minimum: Optional[int] = 0
    maximum_score: int
    created_at: datetime
    updated_at: datetime


@strawberry.input(description="Course Allocation Input")
class CourseAllocationInput:
    uid: Optional[str] = None
    program_course_uid: str
    staff_uid: str


@strawberry.type(description="Course Allocation")
class CourseAllocationNode:
    id: int
    uid: str
    program_course_id: str
    program_course: ProgramCourseNode
    staff_uid: str


@strawberry.input(description="Course Assessment Input")
class ProgramCourseAssessmentInput:
    uid: Optional[str] = None
    program_course_id: int
    exam_category_uid: str
    minimum_exams: int
    can_exceed_minimum_by: Optional[int] = 0
    maximum_score: int


@strawberry.type(description="Program Course Assessment Input")
class ProgramCourseAssessmentNode:
    id: int
    uid: str
    program_course_id: int
    program_course: ProgramCourseNode
    exam_category_uid: str
    minimum_exams: int
    can_exceed_minimum_by: Optional[int] = 0
    maximum_score: int


@strawberry.input(description="Pagination Input")
class PaginationInput:
    offset: int = 0
    limit: int = 10
    search: Optional[str] = None


############ An output for Paginated Course #######################
@strawberry.type(description="Paginated Course")
class PaginatedCourse:
    items: List[CourseNode]
    total_count: int

############ An output for Paginated Course Allocation ############
@strawberry.type(description="Paginated Course Allocation")
class PaginatedCourseAllocation:
    items: List[CourseAllocationNode]
    total_count: int

############ An output for Paginated Course Category ###############
@strawberry.type(description="Paginated Course Category")
class PaginatedCourseCategory:
    items: List[CourseCategoryNode]
    total_count: int

############ An output for Paginated Course Learn Outcome ###############
@strawberry.type(description="Paginated Course Learn Outcome")
class PaginatedCourseLearnOutcome:
    items: List[CourseLearnOutcomeNode]
    total_count: int

############ An output for Paginated Course #######################
@strawberry.type(description="Paginated Program Course Outcome")
class PaginatedProgramCourse:
    items: List[ProgramCourseNode]
    total_count: int

############ An output for Paginated Course Allocation ############
@strawberry.type(description="Paginated Course Allocation")
class PaginatedProgramCourseAssessment:
    items: List[ProgramCourseAssessmentNode]
    total_count: int

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
