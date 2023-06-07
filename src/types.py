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
    start_date: str
    end_date: str


@strawberry.type(description="Academic Year")
class AcademicYearNode:
    uid: str
    name: str
    status: int
    start_date: str
    end_date: str


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
    uid: str
    reg_no: str


@strawberry.input(description="Staff Input")
class StaffInput:
    uid: Optional[str] = None
    pf_number: str


@strawberry.type(description="Staff")
class StaffNode:
    uid: str
    pf_number: str


@strawberry.input(description="Group Input")
class GroupInput:
    uid: Optional[str] = None
    name: str
    code: str


@strawberry.type(description="Staff")
class GroupNode:
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
    moodle_id: Optional[str] = None


@strawberry.type(description="Course Output")
class CourseNode:
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


@strawberry.type(description="Program Semester output")
class ProgramSemesterNode:
    uid: str
    program_id: str
    academic_year_id: str
    study_year: int
    semester: int
    core_credits: float
    elective_credits: float


@strawberry.input(description="Program Input")
class ProgramInput:
    uid: Optional[str] = None
    program_category_uid: str
    code: str
    tcu_code: Optional[str] = None
    nacte_code: Optional[str] = None
    name: str
    short_name: str
    duration: Optional[int] = 0
    moodle_id: Optional[str] = None
    registration_code: Optional[str] = None
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
    uid: str
    description: str
    name: str


@strawberry.type(description="Course Category paginated output")
class CourseCategoryListNode:
    items: List[CourseCategoryNode]
    total_count: int


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
    moodle_id: Optional[str] = None


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


@strawberry.type(description="Program Course paginated Output")
class ProgramCourseListNode:
    items: List[ProgramCourseNode]
    total_count: int


@strawberry.input(description="Course Learn Outcome Input")
class CourseLearnOutcomeInput:
    uid: Optional[str] = None
    course_uid: str
    learning_outcome: str


@strawberry.type(description="Course Learn Outcome Output")
class CourseLearnOutcomeNode:
    uid: str
    course: CourseNode
    learning_outcome: str


@strawberry.type(description="Program Course learning outcome paginated Output")
class CourseLearnOutcomeListNode:
    items: List[CourseLearnOutcomeNode]
    total_count: int


@strawberry.input(description="Program Course Assessment Input")
class ProgramCourseAssessmentInput:
    uid: Optional[str] = None
    program_course_uid: str
    exam_category_uid: str
    minimum_exams: int
    can_exceed_minimum: Optional[int] = 0
    maximum_score: int


@strawberry.type(description="Program Course Assessment Output")
class ProgramCourseAssessmentNode:
    uid: str
    program_course_uid: str
    program_course: ProgramCourseNode
    exam_category_uid: str
    minimum_exams: int
    can_exceed_minimum: Optional[int] = 0
    maximum_score: int


@strawberry.type(description="Program Course Assessment paginated Output")
class ProgramCourseAssessmentListNode:
    items: List[ProgramCourseAssessmentNode]
    total_count: int


@strawberry.input(description="Course Allocation Input")
class CourseAllocationInput:
    uid: Optional[str] = None
    program_course_uid: str
    staff_uid: str


@strawberry.type(description="Course Allocation")
class CourseAllocationNode:
    uid: str
    program_course_uid: str
    program_course: ProgramCourseNode
    staff_uid: str


@strawberry.type(description="Program Allocation Assessment paginated Output")
class CourseAllocationListNode:
    items: List[CourseAllocationNode]
    total_count: int


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


@strawberry.input(description="Control Number Input")
class ControlNumberInput:
    program_code: str
    year_of_study: int
    study_level: str
    student_status: str
    countrycode: int
    registration_number: str
    program_name: str
    system: str


@strawberry.input(description="Fee Structure Input")
class FeeStructureInput:
    program_code: str
    year_of_study: int
    study_level: str
    student_status: str
    countrycode: int


@strawberry.type(description="Fee Structure Output")
class FeeStructureNode:
    name: str
    amount: float
    min_amount: float
    currency: str
    program: ProgramNode


@strawberry.input(description="Control Numbers Input")
class ControlNumberInput:
    program_code: str
    year_of_study: float
    study_level: str
    student_status: str
    countrycode: int
    registration_number: str
    program_name: str
    system: str


@strawberry.type(description="Control Numbers Output")
class ControlNumberNode:
    program_code: str
    year_of_study: float
    study_level: str
    student_status: str
    countrycode: int
    registration_number: str
    program_name: str
    system: str


LoginResult = strawberry.union("LoginResult", types=(LoginSuccess, LoginError))
