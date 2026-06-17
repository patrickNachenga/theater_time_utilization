from __future__ import annotations
import strawberry
from typing import List, Optional
from ..procedure_delay_category.types import ProcedureDelayCategoryNode
from ..procedure_delay_cause.types import ProcedureDelayCauseNode


@strawberry.input
class TheatreRecordDelayInput:
    uid: Optional[str] = None
    delay_cause_uid: str
    description: Optional[str] = None


@strawberry.type
class TheatreRecordDelayNode:
    uid: str
    cause: Optional[ProcedureDelayCauseNode]
    description: Optional[str]


@strawberry.type
class TheatreRecordDelayListNode:
    items: List[TheatreRecordDelayNode]
    total_count: int