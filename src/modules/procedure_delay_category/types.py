import strawberry
from typing import List, Optional


@strawberry.input
class ProcedureDelayCategoryInput:
    uid: Optional[str] = None
    name: str
    code: str


@strawberry.type
class ProcedureDelayCategoryNode:
    uid: str
    name: str
    code: Optional[str]


@strawberry.type
class ProcedureDelayCategoryListNode:
    items: List[ProcedureDelayCategoryNode]
    total_count: int
