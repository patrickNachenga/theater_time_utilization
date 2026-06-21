import strawberry
from typing import List, Optional


@strawberry.type
class AnalyticsStatsNode:
    total_procedures: int
    total_theatre_hours: float
    avg_procedure_minutes: float
    delay_rate: float
    on_time_percentage: float
    mortality_rate: float
    missed_estimate_rate: float


@strawberry.type
class ProceduresOverTimeItemNode:
    date: str
    procedures: int


@strawberry.type
class ProceduresOverTimeListNode:
    items: List[ProceduresOverTimeItemNode]


@strawberry.type
class PieChartItemNode:
    name: str
    value: int
    color: str


@strawberry.type
class PieChartListNode:
    items: List[PieChartItemNode]


@strawberry.type
class TheatreUtilizationItemNode:
    name: str
    utilization: float


@strawberry.type
class TheatreUtilizationListNode:
    items: List[TheatreUtilizationItemNode]


@strawberry.type
class EstimatedVsActualItemNode:
    procedure: str
    estimated: float
    actual: float


@strawberry.type
class EstimatedVsActualListNode:
    items: List[EstimatedVsActualItemNode]


@strawberry.type
class DelaysOverTimeItemNode:
    date: str
    on_time: int
    delayed: int


@strawberry.type
class DelaysOverTimeListNode:
    items: List[DelaysOverTimeItemNode]


@strawberry.type
class DurationDistributionItemNode:
    name: str
    value: int
    color: str


@strawberry.type
class DurationDistributionListNode:
    items: List[DurationDistributionItemNode]


@strawberry.type
class ProceduresByRegionItemNode:
    name: str
    count: int


@strawberry.type
class ProceduresByRegionListNode:
    items: List[ProceduresByRegionItemNode]


@strawberry.type
class TeamPerformanceItemNode:
    team: str
    procedures: int
    avg_duration: float
    delay_rate: float
    on_time_pct: float


@strawberry.type
class TeamPerformanceListNode:
    items: List[TeamPerformanceItemNode]


@strawberry.type
class ProceduresHeatmapItemNode:
    day: str
    hour: str
    count: int


@strawberry.type
class ProceduresHeatmapListNode:
    items: List[ProceduresHeatmapItemNode]