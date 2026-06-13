from __future__ import annotations
import strawberry
from typing import List, Optional
from ..procedure_delay_category.types import ProcedureDelayCategoryNode
from ..procedure_delay_cause.types import ProcedureDelayCauseNode


@strawberry.input
class TheatreRecordDelayInput:
    uid: Optional[str] = None
    record_uid: str
    procedure_delay_category_uid: Optional[str] = None
    delay_cause_uid: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    record_id: Optional[int] = None
    procedure_delay_category_id: Optional[int] = None
    delay_cause_id: Optional[int] = None


@strawberry.type
class TheatreRecordDelayNode:
    uid: str
    procedure_delay_category: Optional[ProcedureDelayCategoryNode]
    delay_cause: Optional[ProcedureDelayCauseNode]
    description: Optional[str]
    sort_order: Optional[int]


@strawberry.type
class TheatreRecordDelayListNode:
    items: List[TheatreRecordDelayNode]
    total_count: int