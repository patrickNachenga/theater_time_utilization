from src.modules.academic_year.types import AcademicYearNode


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
    status: int


@strawberry.type(description="Academic Year")
class AcademicYearSemesterNode:
    status: int
    odd_start_date: str
    odd_end_date: str
    even_start_date: str
    even_end_date: str
    exam_start_date: str
    exam_ticket_date: str
    semester: int
    academic_year: AcademicYearNode
    uid: Optional[str] = None


@strawberry.type(description="AcademicYear Country")
class AcademicYearSemesterListNode:
    items: List[AcademicYearSemesterNode]
    total_count: int
