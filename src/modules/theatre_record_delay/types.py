import strawberry
from typing import List, Optional


@strawberry.input
class TheatreRecordDelayInput:
    uid: Optional[str] = None
    record_uid: str
    procedure_delay_category_uid: Optional[str] = None
    delay_cause_uid: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


@strawberry.type
class TheatreRecordDelayNode:
    uid: str
    record_uid: str
    procedure_delay_category_uid: Optional[str]
    delay_cause_uid: Optional[str]
    description: Optional[str]
    sort_order: Optional[int]


@strawberry.type
class TheatreRecordDelayListNode:
    items: List[TheatreRecordDelayNode]
    total_count: int
