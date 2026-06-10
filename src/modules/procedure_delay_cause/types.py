import strawberry
from typing import List, Optional


@strawberry.input
class ProcedureDelayCauseInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    procedure_delay_category_uid: Optional[str] = None


@strawberry.type
class ProcedureDelayCauseNode:
    uid: str
    name: str
    code: Optional[str]
    description: Optional[str]
    procedure_delay_category_uid: Optional[str]


@strawberry.type
class ProcedureDelayCauseListNode:
    items: List[ProcedureDelayCauseNode]
    total_count: int
