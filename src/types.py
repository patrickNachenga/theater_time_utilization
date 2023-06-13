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
class ExamCategoryGroupsInput:
    uid: Optional[str] = None
    name: str


@strawberry.type(description="Exam category Groups Output")
class ExamCategoryGroupsNode:
    uid: str
    name: str


@strawberry.input(description="Exam Category Input")
class ExamCategoryInput:
    uid: Optional[str] = None
    name: str
    code: str
    exam_category_group_uid: str


@strawberry.type(description="Exam Category Output")
class ExamCategoryNode:
    uid: str
    name: str
    code: str
    exam_category_group: ExamCategoryGroupsNode


@strawberry.input(description="Exam Result Input")
class ExamResultInput:
    uid: Optional[str] = None
    student_uid: str
    program_course_id: int
    exam_category_id: int
    score: float
    out_of: float
    weight: int
    overall_marks: int


@strawberry.type(description="Exam Result Output | Node")
class ExamResultNode:
    student_uid: str
    program_course_id: int
    exam_category_id: int
    score: float
    out_of: float
    weight: int
    overall_marks: float


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


@strawberry.type(description="Exam Category Output")
class ExamCategoryNode:
    uid: str
    name: str
    code: str
    exam_category_group: ExamCategoryGroupsNode


@strawberry.type(description="Exam Category paginated Output")
class ExamCategoryListNode:
    items: List[ExamCategoryNode]
    total_count: int


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
    tcu_code: Optional[str]
    nacte_code: Optional[str]
    duration: Optional[int]
    registration_code: str
    program_category: ProgramCategoryNode
    department_uid: str
    moodle_id: Optional[str]
    registration_code: Optional[str]


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


@strawberry.type(description="Program Course Assessment Output")
class ProgramCourseAssessmentNode2:
    uid: str
    exam_category_uid: str
    minimum_exams: int
    can_exceed_minimum_by: Optional[int] = 0
    maximum_score: int


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
    program_course_assessments: List[ProgramCourseAssessmentNode2]


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
    can_exceed_minimum_by: Optional[int] = 0
    maximum_score: int


@strawberry.type(description="Program Course Assessment Output")
class ProgramCourseAssessmentNode:
    uid: str
    program_course: ProgramCourseNode
    exam_category: ExamCategoryNode
    minimum_exams: int
    can_exceed_minimum_by: Optional[int] = 0
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


@strawberry.input(description="Fee Structure Input")
class FeeStructureInput:
    program_uid: str
    year_of_study: int
    student_status: str
    countrycode: str


@strawberry.type(description="Fee Structure Output")
class FeeStructureNode:
    name: str
    amount: float
    min_amount: float
    currency: str
    program: ProgramNode
    study_year: int


@strawberry.input(description="Renew Control Numbers Input")
class RewControlNumberInput:
    registration_number: str
    pay_type: str
    bill_id: str


@strawberry.input(description="Request Control Numbers Input")
class RequestControlNumberInput:
    program_uid: str
    year_of_study: float
    student_status: str
    countrycode: int
    registration_number: str


@strawberry.type(description="Request Control Numbers Output")
class RequestControlNumberNode:
    program_code: str
    year_of_study: float
    study_level: str
    student_status: str
    countrycode: int
    registration_number: str
    program_name: str
    system: str


@strawberry.input(description="Control Numbers Input")
class ControlNumberInput:
    registration_number: str
    fee_name: str
    amount: float
    control_number: str
    currency: str
    pay_type: str
    academic_year: str
    billid: str


@strawberry.type(description="Control Numbers Output")
class ControlNumberNode:
    registration_number: str
    fee_name: str
    amount: float
    control_number: str
    currency: str
    pay_type: str
    academic_year: str
    bill_id: str


LoginResult = strawberry.union("LoginResult", types=(LoginSuccess, LoginError))


@strawberry.type(description="Program capacity")
class ProgramCapacityNode:
    uid: str
    academic_year: AcademicYearNode
    program: ProgramNode


@strawberry.type(description="Program capacity list")
class ProgramCapacityListNode:
    items: List[ProgramCapacityNode]
    total_count: int


@strawberry.input(description="Program capacity input")
class ProgramCapacityInputNode:
    program_uid: str
    academic_year_uid: str
    is_active: bool
    uid: Optional[str]


@strawberry.type(description="Semester registration")
class SemesterRegistrationNode:
    student_uid: str
    study_year: int
    semester_program: ProgramSemesterNode


@strawberry.type(description="Semester registration list")
class SemesterRegistrationListNode:
    items: List[SemesterRegistrationNode]
    total_count: int


@strawberry.input(description="Register student to semester")
class StudentSemesterRegistrationInputNode:
    student_uid: str
    study_year: int
    program_semester_uid: str


@strawberry.type(description="Course registration Node")
class CourseRegistrationNode:
    student_uid: str
    core_elective: str
    program_course: ProgramCourseNode


@strawberry.type(description="Course registration list")
class CourseRegistrationListNode:
    items: List[CourseRegistrationNode]
    total_count: int


@strawberry.input(description="Course registration input")
class CourseRegistrationInputNode:
    student_uid: str
    core_elective: int
    program_course_uid: str


@strawberry.type
class StudentUaaData:
    registration_number: str
    full_name: str


@strawberry.type
class UaaDataResponse:
    status: bool
    message: str
    code: int
    data: List[StudentUaaData]


@strawberry.input
class RequestProgramSemester:
    registration_number: str
    program_uid: str
    academic_year_uid: str
    study_year: int
    semester: int


@strawberry.type
class InnerStudentProgramSemester:
    registration_number: Optional[str]
    program_id: int
    academic_year_id: int
    study_year: int
    semester: int
    program_semester_id: int
