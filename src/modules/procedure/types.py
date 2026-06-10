import strawberry
from typing import List, Optional


@strawberry.input
class ProcedureInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None
    estimated_minutes: Optional[int] = None


@strawberry.type
class ProcedureNode:
    uid: str
    name: str
    code: Optional[str]
    estimated_minutes: Optional[int]


@strawberry.type
class ProcedureListNode:
    items: List[ProcedureNode]
    total_count: int
