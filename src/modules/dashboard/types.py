import strawberry
from typing import List, Optional


@strawberry.type
class DashboardStatsNode:
    total_records: int
    delay_rate: float
    avg_procedure_minutes: float
    missed_estimate_rate: float


@strawberry.type
class DelayDistributionItemNode:
    label: str
    count: int
    color: str


@strawberry.type
class DelayDistributionListNode:
    items: List[DelayDistributionItemNode]


@strawberry.type
class TheatreUnitActivityItemNode:
    label: str
    count: int
    color: Optional[str] = None


@strawberry.type
class TheatreUnitActivityListNode:
    items: List[TheatreUnitActivityItemNode]