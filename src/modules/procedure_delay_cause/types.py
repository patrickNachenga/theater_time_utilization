import strawberry
from typing import List, Optional
from ..procedure_delay_category.types import ProcedureDelayCategoryNode


@strawberry.input
class ProcedureDelayCauseInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    procedure_delay_category_uid: Optional[str] = None
    procedure_delay_category_id: Optional[int] = None


@strawberry.type
class ProcedureDelayCauseNode:
    uid: str
    name: str
    code: Optional[str]
    description: Optional[str]
    procedure_delay_category: Optional[ProcedureDelayCategoryNode]


@strawberry.type
class ProcedureDelayCauseListNode:
    items: List[ProcedureDelayCauseNode]
    total_count: int