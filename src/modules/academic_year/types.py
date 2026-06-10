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
