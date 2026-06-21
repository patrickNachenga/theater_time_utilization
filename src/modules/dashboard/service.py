from sqlalchemy import func

from src.database.session import session_scope
from src.models import TheatreProcedureRecord, TheatreRecordDelay, ProcedureDelayCause, ProcedureDelayCategory, TheatreUnit
from src.modules.dashboard.types import (
    DashboardStatsNode,
    DelayDistributionItemNode,
    DelayDistributionListNode,
    TheatreUnitActivityItemNode,
    TheatreUnitActivityListNode,
)
from src.shared.response import Response
from src.shared.response_code import ResponseCode


# Predefined color palette for chart slices
DELAY_COLORS = [
    "#e53935",  # Red
    "#1976d2",  # Blue
    "#ffd700",  # Gold
    "#28a745",  # Green
    "#9c27b0",  # Purple
    "#ff9800",  # Orange
    "#00bcd4",  # Cyan
    "#795548",  # Brown
    "#607d8b",  # Blue Grey
    "#e91e63",  # Pink
]

UNIT_COLORS = [
    "#1976d2",  # Blue
    "#2196f3",  # Light Blue
    "#42a5f5",  # Lighter Blue
    "#64b5f6",  # Lightest Blue
    "#1565c0",  # Dark Blue
    "#0d47a1",  # Deep Blue
    "#1e88e5",  # Mid Blue
    "#90caf9",  # Pale Blue
]


class DashboardService:

    @staticmethod
    def get_dashboard_stats() -> Response[DashboardStatsNode]:
        """
        Compute dashboard statistics:
        - total_records: Count of all theatre procedure records
        - delay_rate: Percentage of records where had_delay is True
        - avg_procedure_minutes: Average duration_minutes across all records
        - missed_estimate_rate: Percentage where variance_minutes > 0
        """
        with session_scope() as session:
            try:
                total_records = session.query(func.count(TheatreProcedureRecord.id)).filter(
                    TheatreProcedureRecord.deleted_at.is_(None)
                ).scalar() or 0

                if total_records == 0:
                    return Response(
                        status=True,
                        code=ResponseCode.SUCCESS,
                        message="Dashboard stats retrieved successfully",
                        data=DashboardStatsNode(
                            total_records=0,
                            delay_rate=0.0,
                            avg_procedure_minutes=0.0,
                            missed_estimate_rate=0.0,
                        ),
                    )

                # Delay rate: percentage of records with had_delay=True
                delay_count = session.query(func.count(TheatreProcedureRecord.id)).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.had_delay.is_(True),
                ).scalar() or 0
                delay_rate = round((delay_count / total_records) * 100, 1)

                # Average procedure duration in minutes
                avg_duration = session.query(func.avg(TheatreProcedureRecord.duration_minutes)).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                ).scalar() or 0
                avg_procedure_minutes = round(float(avg_duration), 1)

                # Missed estimate rate: percentage where variance_minutes > 0 (actual > estimated)
                # Only count records where estimated_duration_minutes is not null
                missed_estimate_count = session.query(func.count(TheatreProcedureRecord.id)).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.estimated_duration_minutes.isnot(None),
                    TheatreProcedureRecord.variance_minutes > 0,
                ).scalar() or 0

                total_with_estimate = session.query(func.count(TheatreProcedureRecord.id)).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.estimated_duration_minutes.isnot(None),
                ).scalar() or 0

                missed_estimate_rate = round(
                    (missed_estimate_count / total_with_estimate) * 100, 1
                ) if total_with_estimate > 0 else 0.0

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Dashboard stats retrieved successfully",
                    data=DashboardStatsNode(
                        total_records=total_records,
                        delay_rate=delay_rate,
                        avg_procedure_minutes=avg_procedure_minutes,
                        missed_estimate_rate=missed_estimate_rate,
                    ),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Unable to retrieve dashboard stats",
                    data=None,
                )

    @staticmethod
    async def get_delay_distribution() -> Response[DelayDistributionListNode]:
        """
        Get delay distribution grouped by delay category.
        Returns count of records for each delay category, plus a "No Delay" count.
        """
        with session_scope() as session:
            try:
                # Get total records count
                total_records = session.query(func.count(TheatreProcedureRecord.id)).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                ).scalar() or 0

                if total_records == 0:
                    return Response(
                        status=True,
                        code=ResponseCode.SUCCESS,
                        message="Delay distribution retrieved successfully",
                        data=DelayDistributionListNode(items=[]),
                    )

                # Count records with no delay
                no_delay_count = session.query(func.count(TheatreProcedureRecord.id)).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.had_delay.is_(False),
                ).scalar() or 0

                # Get delay distribution by category
                # Join: theatre_procedure_records -> theatre_record_delays -> procedure_delay_causes -> procedure_delay_categories
                delay_by_category = (
                    session.query(
                        ProcedureDelayCategory.name,
                        func.count(func.distinct(TheatreProcedureRecord.id)).label("count"),
                    )
                    .join(
                        TheatreRecordDelay,
                        TheatreRecordDelay.record_id == TheatreProcedureRecord.id,
                    )
                    .join(
                        ProcedureDelayCause,
                        ProcedureDelayCause.id == TheatreRecordDelay.cause_id,
                    )
                    .join(
                        ProcedureDelayCategory,
                        ProcedureDelayCategory.id
                        == ProcedureDelayCause.procedure_delay_category_id,
                    )
                    .filter(
                        TheatreProcedureRecord.deleted_at.is_(None),
                        TheatreProcedureRecord.had_delay.is_(True),
                    )
                    .group_by(ProcedureDelayCategory.name)
                    .order_by(
                        func.count(func.distinct(TheatreProcedureRecord.id)).desc()
                    )
                    .all()
                )

                items = []
                color_index = 0

                # Add delay categories
                for name, count in delay_by_category:
                    color = DELAY_COLORS[color_index % len(DELAY_COLORS)]
                    items.append(DelayDistributionItemNode(
                        label=name,
                        count=count,
                        color=color,
                    ))
                    color_index += 1

                # Add "No Delay" at the end with green
                if no_delay_count > 0:
                    items.append(DelayDistributionItemNode(
                        label="No Delay",
                        count=no_delay_count,
                        color="#28a745",
                    ))

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Delay distribution retrieved successfully",
                    data=DelayDistributionListNode(items=items),
                )

            except Exception as e:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Unable to retrieve delay distribution",
                    data=None,
                )

    @staticmethod
    def get_theatre_unit_activity() -> Response[TheatreUnitActivityListNode]:
        """
        Get theatre unit activity grouped by theatre unit.
        Returns count of procedures per unit.
        """
        with session_scope() as session:
            try:
                # Count procedures per theatre unit
                unit_activity = (
                    session.query(
                        TheatreUnit.name,
                        func.count(TheatreProcedureRecord.id).label("count"),
                    )
                    .join(
                        TheatreUnit,
                        TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id,
                    )
                    .filter(
                        TheatreProcedureRecord.deleted_at.is_(None),
                    )
                    .group_by(TheatreUnit.name)
                    .order_by(func.count(TheatreProcedureRecord.id).desc())
                    .all()
                )

                items = []
                for index, (name, count) in enumerate(unit_activity):
                    color = UNIT_COLORS[index % len(UNIT_COLORS)]
                    items.append(TheatreUnitActivityItemNode(
                        label=name,
                        count=count,
                        color=color,
                    ))

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Theatre unit activity retrieved successfully",
                    data=TheatreUnitActivityListNode(items=items),
                )

            except Exception as e:
                print("=============================================>",e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Unable to retrieve theatre unit activity",
                    data=None,
                )


DashboardCrud = DashboardService()