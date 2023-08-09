import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

import strawberry
from pydantic import BaseModel, constr
from sqlalchemy import Date


class ProgramCodeInput(BaseModel):
    code: Optional[str]
    uid: Optional[str]


@strawberry.enum
class Gender(str, Enum):
    Male = 'Male'
    Female = "Female"


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


@strawberry.input(description="Academic Year Input")
class AcademicYearSemesterInput:
    uid: Optional[str] = None
    odd_start_date: str
    odd_end_date: str
    even_start_date: str
    even_end_date: str
    exam_start_date: str
    exam_ticket_date: str
    semester: int
    academic_year_uid: str


@strawberry.type(description="Academic Year")
class AcademicYearSemesterNode:
    uid: Optional[str] = None
    odd_start_date: str
    odd_end_date: str
    even_start_date: str
    even_end_date: str
    exam_start_date: str
    exam_ticket_date: str
    semester: int
    academic_year: AcademicYearNode


@strawberry.type(description="AcademicYear Country")
class AcademicYearSemesterListNode:
    items: List[AcademicYearSemesterNode]
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


@strawberry.input(description="Exam Result Summary Input")
class ExamResultSummaryInput:
    uid: str
    program_course_id: int
    exam_category_id: int
    student_uid: str
    registration_number: str
    student_name: str
    gender: str
    course_code: str
    course_name: str
    credit: float
    grade: str
    grade_point: float
    grade_remark: str
    publish_status: bool
    publisher: str
    publish_date: str


@strawberry.type(description="Exam Result Summary Node|Output")
class ExamResultSummaryNode:
    uid: Optional[str] = None
    program_course_id: int
    exam_category_id: int
    student_uid: str
    registration_number: str
    student_name: str
    gender: str
    course_code: str
    course_name: str
    credit: float
    grade: str
    grade_point: float
    grade_remark: str
    publish_status: bool
    publisher: str


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
    description: Optional[str] = ""
    name: str
    offered: Optional[int] = 1
    department_uid: str
    moodle_id: Optional[str] = ""


@strawberry.type(description="Course Output")
class CourseNode:
    uid: str
    code: str
    description: str
    name: str
    offered: int
    department_uid: str
    moodle_id: Optional[str]


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
    id: int
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
    program_course: "ProgramCourseNode"
    exam_category: ExamCategoryNode
    minimum_exams: int
    can_exceed_minimum_by: Optional[int] = 0
    maximum_score: int


@strawberry.type(description="Program Course Assessment paginated Output")
class ProgramCourseAssessmentListNode:
    items: List[ProgramCourseAssessmentNode]
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
    program_semester: "ProgramSemesterNode"
    course: CourseNode
    course_category: "CourseCategoryNode"
    credit: float
    lecture_hours: float
    seminar_hours: float
    practical_hours: float
    assignment_hours: float
    independent_study_hours: float
    pass_hours: float
    moodle_id: Optional[str]
    program_course_assessments: List[ProgramCourseAssessmentNode]


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


@strawberry.input(description="Course Allocation Input")
class CourseAllocationInput:
    uid: Optional[str] = None
    program_course_uid: str
    staff_uid: str


@strawberry.type(description="Course Allocation")
class CourseAllocationNode:
    uid: str | None
    program_course_uid: str | None
    program_course: ProgramCourseNode | None
    staff_uid: str | None


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
    uid: str
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
    data: List[StudentUaaData] | None


@strawberry.input(description="Allocation template input")
class AllocationTemplateNode:
    allocation_uid: str
    assessment_number: int


@strawberry.scalar
class Base64String:
    @staticmethod
    def serialize(value):
        return value


@strawberry.type
class ExcelFile:
    base64_data: Base64String


@strawberry.input
class RequestProgramSemester:
    registration_number: str
    program_uid: str
    academic_year_uid: str
    study_year: int
    semester: int


@strawberry.input
class StaffCourseAllocationBySemesterInputs:
    staff_uid: str
    is_current: int
    semester: int


@strawberry.type(description="Course Allocation By semester")
class StaffCourseAllocationBySemesterNode:
    uid: str | None
    program_course_uid: str | None
    program_course: ProgramCourseNode | None
    staff_uid: str | None


@strawberry.type
class InnerStudentProgramSemester:
    program_id: int
    academic_year_id: int
    study_year: int
    semester: int


@strawberry.input(description="Staff Allocation input")
class StaffAllocationInputNode:
    program_course_uid: Optional[str]
    staff_uid: str
    is_current: int


@strawberry.input(description="Course to register input")
class CourseRegisterInputNode:
    study_year: int
    program_uid: str
    semester: int
    student_uid: str


@strawberry.type(description="Program Course paginated Output")
class StudentProgramCourseListNode:
    course_to_register: List[ProgramCourseNode]
    total_count: int
    course_registered: List[CourseRegistrationNode]


@strawberry.type(description="Program Course paginated Output")
class ProgramCourseListNode:
    items: List[ProgramCourseNode]
    total_count: int


@strawberry.input(description="Course Allocation Staff update Input")
class CourseAllocationStaffUpdateInput:
    uid: str
    staff_uid: str


@strawberry.input(description="Get moodle url")
class MoodleGetUrlInput:
    moodle_username: str
    course_moodle_id: Optional[str]


@strawberry.input(description="Program Course update can_exceed_minimum_by input")
class ProgramCourseAssessmentUpdateExceedInput:
    program_course_assessment_uid: str
    can_exceed_minimum_by: str


@strawberry.input(description="Exam registration input")
class ExamRegistrationInput:
    type: int
    course_registration_uid: str


@strawberry.type(description="Exam registration Output")
class ExamRegistrationNode:
    exam_category: ExamCategoryNode
    student_course_registration: CourseRegistrationNode


@strawberry.type(description="Exam registration Output")
class ExamRegistrationListNode:
    items: List[ExamRegistrationNode]
    total_count: int


@strawberry.type(description="Exam failure Output")
class ExamFailureNode:
    is_attended: bool
    student_exam_registration: ExamRegistrationNode
    type: int


@strawberry.type(description="Exam Postponement Output")
class ExamPostponementNode:
    type: int
    student_course_registrations: CourseRegistrationNode
    is_resumed: bool
    reason: str
    approved_uid: str


@strawberry.type(description="Exam to register Output")
class ExamToRegister:
    first_sitting: List[CourseRegistrationNode]
    failure: List[ExamFailureNode]
    postponed: List[ExamPostponementNode]
