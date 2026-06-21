from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from src.database.session import session_scope
from src.models import (
    TheatreProcedureRecord,
    TheatreRecordDelay,
    ProcedureDelayCause,
    ProcedureDelayCategory,
    TheatreUnit,
    Procedure,
    Region,
    TheatreRecordTeamMember,
    TheatreMember,
    TheatreRole,
)
from src.models.theatre_procedure_record import PatientOutcome, PatientType
from src.modules.analytics.types import (
    AnalyticsStatsNode,
    ProceduresOverTimeItemNode,
    ProceduresOverTimeListNode,
    PieChartItemNode,
    PieChartListNode,
    TheatreUtilizationItemNode,
    TheatreUtilizationListNode,
    EstimatedVsActualItemNode,
    EstimatedVsActualListNode,
    DelaysOverTimeItemNode,
    DelaysOverTimeListNode,
    DurationDistributionItemNode,
    DurationDistributionListNode,
    ProceduresByRegionItemNode,
    ProceduresByRegionListNode,
    TeamPerformanceItemNode,
    TeamPerformanceListNode,
    ProceduresHeatmapItemNode,
    ProceduresHeatmapListNode,
)
from src.shared.response import Response
from src.shared.response_code import ResponseCode


# Predefined color palette for chart slices
CHART_COLORS = [
    "#2563eb",  # Blue
    "#dc2626",  # Red
    "#16a34a",  # Green
    "#f59e0b",  # Amber
    "#8b5cf6",  # Purple
    "#ec4899",  # Pink
    "#06b6d4",  # Cyan
    "#f97316",  # Orange
    "#14b8a6",  # Teal
    "#6366f1",  # Indigo
    "#e11d48",  # Rose
    "#65a30d",  # Lime
]

# Duration range labels and their min/max in minutes
DURATION_RANGES = [
    ("0-30 min", 0, 30),
    ("30-60 min", 30, 60),
    ("60-120 min", 60, 120),
    ("120-180 min", 120, 180),
    ("180-240 min", 180, 240),
    ("240+ min", 240, 999999),
]

# Day order for heatmap
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

HOUR_SLOTS = [
    "08:00–10:00",
    "10:00–12:00",
    "12:00–14:00",
    "14:00–16:00",
    "16:00–18:00",
]


def _apply_date_range_filter(query, date_range=None):
    """Apply a date range filter to a query (optional filter, returns all records when None)."""
    if date_range and date_range != "All Time":
        now = datetime.utcnow()
        if date_range == "Today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0).date()
        elif date_range == "This Week":
            start_date = (now - timedelta(days=now.weekday())).date()
        elif date_range == "This Month":
            start_date = now.replace(day=1).date()
        elif date_range == "This Quarter":
            quarter_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_month, day=1).date()
        elif date_range == "This Year":
            start_date = now.replace(month=1, day=1).date()
        elif date_range == "Last 7 Days":
            start_date = (now - timedelta(days=7)).date()
        elif date_range == "Last 30 Days":
            start_date = (now - timedelta(days=30)).date()
        elif date_range == "Last 90 Days":
            start_date = (now - timedelta(days=90)).date()
        else:
            # Default: no filter
            return query
        query = query.filter(TheatreProcedureRecord.procedure_date >= start_date)
    return query


def _apply_theatre_unit_filter(query, theatre_unit_uid=None):
    """Apply a theatre unit filter to a query."""
    if theatre_unit_uid:
        query = query.filter(TheatreUnit.uid == theatre_unit_uid)
    return query


def _apply_procedure_filter(query, procedure_uid=None):
    """Apply a procedure filter to a query."""
    if procedure_uid:
        query = query.filter(Procedure.uid == procedure_uid)
    return query


class AnalyticsService:

    @staticmethod
    def get_analytics_stats(date_range: str = None, theatre_unit_uid: str = None) -> Response[AnalyticsStatsNode]:
        """Get overall analytics KPI stats."""
        with session_scope() as session:
            try:
                base_query = session.query(TheatreProcedureRecord).filter(
                    TheatreProcedureRecord.deleted_at.is_(None)
                )

                # Apply date range filter
                if date_range and date_range != "All Time":
                    now = datetime.utcnow()
                    if date_range == "Today":
                        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0).date()
                    elif date_range == "This Week":
                        start_date = (now - timedelta(days=now.weekday())).date()
                    elif date_range == "This Month":
                        start_date = now.replace(day=1).date()
                    elif date_range == "This Quarter":
                        quarter_month = ((now.month - 1) // 3) * 3 + 1
                        start_date = now.replace(month=quarter_month, day=1).date()
                    elif date_range == "This Year":
                        start_date = now.replace(month=1, day=1).date()
                    elif date_range == "Last 7 Days":
                        start_date = (now - timedelta(days=7)).date()
                    elif date_range == "Last 30 Days":
                        start_date = (now - timedelta(days=30)).date()
                    elif date_range == "Last 90 Days":
                        start_date = (now - timedelta(days=90)).date()
                    else:
                        start_date = None
                    if start_date:
                        base_query = base_query.filter(TheatreProcedureRecord.procedure_date >= start_date)

                # Apply theatre unit filter
                if theatre_unit_uid:
                    base_query = base_query.join(TheatreUnit).filter(TheatreUnit.uid == theatre_unit_uid)

                # Total procedures
                total_procedures = base_query.count()

                if total_procedures == 0:
                    return Response(
                        status=True,
                        code=ResponseCode.SUCCESS,
                        message="Analytics stats retrieved successfully",
                        data=AnalyticsStatsNode(
                            total_procedures=0,
                            total_theatre_hours=0.0,
                            avg_procedure_minutes=0.0,
                            delay_rate=0.0,
                            on_time_percentage=0.0,
                            mortality_rate=0.0,
                            missed_estimate_rate=0.0,
                        ),
                    )

                # Total theatre hours (sum of duration_minutes / 60)
                total_minutes = base_query.with_entities(
                    func.coalesce(func.sum(TheatreProcedureRecord.duration_minutes), 0)
                ).scalar() or 0
                total_theatre_hours = round(float(total_minutes) / 60, 1)

                # Average procedure duration in minutes
                avg_duration = base_query.with_entities(
                    func.coalesce(func.avg(TheatreProcedureRecord.duration_minutes), 0)
                ).scalar() or 0
                avg_procedure_minutes = round(float(avg_duration), 1)

                # Delay rate
                delay_count = base_query.filter(
                    TheatreProcedureRecord.had_delay.is_(True)
                ).count()
                delay_rate = round((delay_count / total_procedures) * 100, 1)
                on_time_percentage = round(100.0 - delay_rate, 1)

                # Mortality rate
                death_count = base_query.filter(
                    TheatreProcedureRecord.outcome == PatientOutcome.DEATH
                ).count()
                mortality_rate = round((death_count / total_procedures) * 100, 1)

                # Missed estimate rate (actual > estimated)
                total_with_estimate = base_query.filter(
                    TheatreProcedureRecord.estimated_duration_minutes.isnot(None)
                ).count()

                if total_with_estimate > 0:
                    missed_estimate_count = base_query.filter(
                        TheatreProcedureRecord.estimated_duration_minutes.isnot(None),
                        TheatreProcedureRecord.variance_minutes > 0,
                    ).count()
                    missed_estimate_rate = round((missed_estimate_count / total_with_estimate) * 100, 1)
                else:
                    missed_estimate_rate = 0.0

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Analytics stats retrieved successfully",
                    data=AnalyticsStatsNode(
                        total_procedures=total_procedures,
                        total_theatre_hours=total_theatre_hours,
                        avg_procedure_minutes=avg_procedure_minutes,
                        delay_rate=delay_rate,
                        on_time_percentage=on_time_percentage,
                        mortality_rate=mortality_rate,
                        missed_estimate_rate=missed_estimate_rate,
                    ),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve analytics stats",
                    data=None,
                )

    @staticmethod
    def get_procedures_over_time(
        date_range: str = None,
        theatre_unit_uid: str = None,
        procedure_uid: str = None,
    ) -> Response[ProceduresOverTimeListNode]:
        """Get procedure count over time (grouped by date)."""
        with session_scope() as session:
            try:
                query = session.query(
                    TheatreProcedureRecord.procedure_date,
                    func.count(TheatreProcedureRecord.id).label("procedures"),
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                )

                query = _apply_date_range_filter(query, date_range)

                if theatre_unit_uid or procedure_uid:
                    query = query.join(Procedure, Procedure.id == TheatreProcedureRecord.procedure_id)
                    query = query.join(TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id)

                query = _apply_theatre_unit_filter(query, theatre_unit_uid)
                query = _apply_procedure_filter(query, procedure_uid)

                results = query.group_by(
                    TheatreProcedureRecord.procedure_date
                ).order_by(
                    TheatreProcedureRecord.procedure_date.asc()
                ).all()

                items = [
                    ProceduresOverTimeItemNode(
                        date=str(result.procedure_date),
                        procedures=result.procedures,
                    )
                    for result in results
                ]

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Procedures over time retrieved successfully",
                    data=ProceduresOverTimeListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve procedures over time",
                    data=None,
                )

    @staticmethod
    def get_patient_type_distribution(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[PieChartListNode]:
        """Get distribution of Emergency vs Elective patients."""
        with session_scope() as session:
            try:
                query = session.query(
                    TheatreProcedureRecord.patient_type,
                    func.count(TheatreProcedureRecord.id).label("value"),
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                )

                query = _apply_date_range_filter(query, date_range)

                if theatre_unit_uid:
                    query = query.join(TheatreUnit).filter(TheatreUnit.uid == theatre_unit_uid)

                results = query.group_by(
                    TheatreProcedureRecord.patient_type
                ).all()

                items = []
                for result in results:
                    name = result.patient_type.value if hasattr(result.patient_type, 'value') else str(result.patient_type)
                    color = "#dc2626" if name == "EMERGENCY" else "#2563eb"
                    items.append(PieChartItemNode(
                        name=name.capitalize(),
                        value=result.value,
                        color=color,
                    ))

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Patient type distribution retrieved successfully",
                    data=PieChartListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve patient type distribution",
                    data=None,
                )

    @staticmethod
    def get_patient_outcomes(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[PieChartListNode]:
        """Get distribution of Discharged vs Deceased patients."""
        with session_scope() as session:
            try:
                query = session.query(
                    TheatreProcedureRecord.outcome,
                    func.count(TheatreProcedureRecord.id).label("value"),
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                )

                query = _apply_date_range_filter(query, date_range)

                if theatre_unit_uid:
                    query = query.join(TheatreUnit).filter(TheatreUnit.uid == theatre_unit_uid)

                results = query.group_by(
                    TheatreProcedureRecord.outcome
                ).all()

                items = []
                for result in results:
                    name = result.outcome.value if hasattr(result.outcome, 'value') else str(result.outcome)
                    color = "#16a34a" if name == "DISCHARGED" else "#dc2626"
                    items.append(PieChartItemNode(
                        name=name.capitalize(),
                        value=result.value,
                        color=color,
                    ))

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Patient outcomes retrieved successfully",
                    data=PieChartListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve patient outcomes",
                    data=None,
                )

    @staticmethod
    def get_theatre_utilization(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[TheatreUtilizationListNode]:
        """Get utilization percentage per theatre unit."""
        with session_scope() as session:
            try:
                base_query = session.query(TheatreProcedureRecord).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                )
                base_query = _apply_date_range_filter(base_query, date_range)

                if theatre_unit_uid:
                    base_query = base_query.join(TheatreUnit).filter(TheatreUnit.uid == theatre_unit_uid)

                # Calculate total available minutes per unit
                # Utilization = (total procedure duration / total available time) * 100
                # Assume 10 hours (600 min) per day per unit as available time
                available_minutes_per_day = 600  # 10 hours

                # Get procedure minutes per unit
                unit_stats = (
                    session.query(
                        TheatreUnit.name,
                        func.coalesce(func.sum(TheatreProcedureRecord.duration_minutes), 0).label("total_minutes"),
                        func.count(func.distinct(TheatreProcedureRecord.procedure_date)).label("active_days"),
                    )
                    .select_from(TheatreProcedureRecord)
                    .join(TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id)
                    .filter(TheatreProcedureRecord.deleted_at.is_(None))
                )

                unit_stats = _apply_date_range_filter(unit_stats, date_range)

                if theatre_unit_uid:
                    unit_stats = unit_stats.filter(TheatreUnit.uid == theatre_unit_uid)

                unit_stats = unit_stats.group_by(TheatreUnit.name).all()

                items = []
                for name, total_minutes, active_days in unit_stats:
                    total_available = active_days * available_minutes_per_day
                    utilization = round(
                        (float(total_minutes) / total_available) * 100, 1
                    ) if total_available > 0 else 0.0
                    utilization = min(utilization, 100.0)  # Cap at 100%
                    items.append(TheatreUtilizationItemNode(
                        name=name,
                        utilization=utilization,
                    ))

                # Sort by utilization descending
                items.sort(key=lambda x: x.utilization, reverse=True)

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Theatre utilization retrieved successfully",
                    data=TheatreUtilizationListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve theatre utilization",
                    data=None,
                )

    @staticmethod
    def get_estimated_vs_actual_duration(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[EstimatedVsActualListNode]:
        """Get estimated vs actual duration per procedure type."""
        with session_scope() as session:
            try:
                query = session.query(
                    Procedure.name,
                    func.coalesce(func.avg(TheatreProcedureRecord.estimated_duration_minutes), 0).label("estimated"),
                    func.coalesce(func.avg(TheatreProcedureRecord.duration_minutes), 0).label("actual"),
                ).select_from(TheatreProcedureRecord).join(
                    Procedure, Procedure.id == TheatreProcedureRecord.procedure_id
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.estimated_duration_minutes.isnot(None),
                )

                query = _apply_date_range_filter(query, date_range)

                if theatre_unit_uid:
                    query = query.join(TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id)
                    query = query.filter(TheatreUnit.uid == theatre_unit_uid)

                results = query.group_by(Procedure.name).order_by(
                    func.avg(TheatreProcedureRecord.duration_minutes).desc()
                ).all()

                items = [
                    EstimatedVsActualItemNode(
                        procedure=name,
                        estimated=round(float(estimated), 1),
                        actual=round(float(actual), 1),
                    )
                    for name, estimated, actual in results
                ]

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Estimated vs actual duration retrieved successfully",
                    data=EstimatedVsActualListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve estimated vs actual duration",
                    data=None,
                )

    @staticmethod
    def get_delays_over_time(
        date_range: str = None,
        theatre_unit_uid: str = None,
        procedure_uid: str = None,
    ) -> Response[DelaysOverTimeListNode]:
        """Get on-time vs delayed procedures per day."""
        with session_scope() as session:
            try:
                # On-time procedures per day
                on_time_query = session.query(
                    TheatreProcedureRecord.procedure_date,
                    func.count(TheatreProcedureRecord.id).label("count"),
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.had_delay.is_(False),
                )

                on_time_query = _apply_date_range_filter(on_time_query, date_range)

                if theatre_unit_uid or procedure_uid:
                    on_time_query = on_time_query.join(Procedure, Procedure.id == TheatreProcedureRecord.procedure_id)
                    on_time_query = on_time_query.join(TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id)

                on_time_query = _apply_theatre_unit_filter(on_time_query, theatre_unit_uid)
                on_time_query = _apply_procedure_filter(on_time_query, procedure_uid)

                on_time_results = on_time_query.group_by(
                    TheatreProcedureRecord.procedure_date
                ).all()
                on_time_map = {str(r.procedure_date): r.count for r in on_time_results}

                # Delayed procedures per day
                delayed_query = session.query(
                    TheatreProcedureRecord.procedure_date,
                    func.count(TheatreProcedureRecord.id).label("count"),
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.had_delay.is_(True),
                )

                delayed_query = _apply_date_range_filter(delayed_query, date_range)

                if theatre_unit_uid or procedure_uid:
                    delayed_query = delayed_query.join(Procedure, Procedure.id == TheatreProcedureRecord.procedure_id)
                    delayed_query = delayed_query.join(TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id)

                delayed_query = _apply_theatre_unit_filter(delayed_query, theatre_unit_uid)
                delayed_query = _apply_procedure_filter(delayed_query, procedure_uid)

                delayed_results = delayed_query.group_by(
                    TheatreProcedureRecord.procedure_date
                ).all()
                delayed_map = {str(r.procedure_date): r.count for r in delayed_results}

                # Merge all dates
                all_dates = sorted(set(list(on_time_map.keys()) + list(delayed_map.keys())))

                items = [
                    DelaysOverTimeItemNode(
                        date=date_str,
                        on_time=on_time_map.get(date_str, 0),
                        delayed=delayed_map.get(date_str, 0),
                    )
                    for date_str in all_dates
                ]

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Delays over time retrieved successfully",
                    data=DelaysOverTimeListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve delays over time",
                    data=None,
                )

    @staticmethod
    def get_duration_distribution(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[DurationDistributionListNode]:
        """Get distribution of procedures by duration range."""
        with session_scope() as session:
            try:
                base_query = session.query(TheatreProcedureRecord).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                )
                base_query = _apply_date_range_filter(base_query, date_range)

                if theatre_unit_uid:
                    base_query = base_query.join(TheatreUnit).filter(TheatreUnit.uid == theatre_unit_uid)

                items = []
                for idx, (label, min_val, max_val) in enumerate(DURATION_RANGES):
                    count = base_query.filter(
                        TheatreProcedureRecord.duration_minutes >= min_val,
                        TheatreProcedureRecord.duration_minutes < max_val,
                    ).count()

                    if count > 0:
                        color = CHART_COLORS[idx % len(CHART_COLORS)]
                        items.append(DurationDistributionItemNode(
                            name=label,
                            value=count,
                            color=color,
                        ))

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Duration distribution retrieved successfully",
                    data=DurationDistributionListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve duration distribution",
                    data=None,
                )

    @staticmethod
    def get_procedures_by_region(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[ProceduresByRegionListNode]:
        """Get procedure count grouped by patient region."""
        with session_scope() as session:
            try:
                query = session.query(
                    Region.name,
                    func.count(TheatreProcedureRecord.id).label("count"),
                ).select_from(TheatreProcedureRecord).join(
                    Region, Region.id == TheatreProcedureRecord.patient_region_id
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                )

                query = _apply_date_range_filter(query, date_range)

                if theatre_unit_uid:
                    query = query.join(TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id)
                    query = query.filter(TheatreUnit.uid == theatre_unit_uid)

                results = query.group_by(Region.name).order_by(
                    func.count(TheatreProcedureRecord.id).desc()
                ).all()

                items = [
                    ProceduresByRegionItemNode(
                        name=name,
                        count=count,
                    )
                    for name, count in results
                ]

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Procedures by region retrieved successfully",
                    data=ProceduresByRegionListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve procedures by region",
                    data=None,
                )

    @staticmethod
    def get_team_performance(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[TeamPerformanceListNode]:
        """Get team performance metrics grouped by team member (surgeon)."""
        with session_scope() as session:
            try:
                from src.models.theatre_procedure_record import TeamRole as TeamRoleEnum

                # Query team member performance
                # Focus on SURGEON team members (using TeamRole enum)
                query = session.query(
                    TheatreMember.name.label("team"),
                    func.count(func.distinct(TheatreProcedureRecord.id)).label("procedures"),
                    func.coalesce(func.avg(TheatreProcedureRecord.duration_minutes), 0).label("avg_duration"),
                ).select_from(TheatreRecordTeamMember).join(
                    TheatreMember, TheatreMember.id == TheatreRecordTeamMember.theatre_member_id
                ).join(
                    TheatreProcedureRecord, TheatreProcedureRecord.id == TheatreRecordTeamMember.record_id
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreRecordTeamMember.deleted_at.is_(None),
                    TheatreRecordTeamMember.role == TeamRoleEnum.SURGEON,
                )

                query = _apply_date_range_filter(query, date_range)

                if theatre_unit_uid:
                    query = query.join(TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id)
                    query = query.filter(TheatreUnit.uid == theatre_unit_uid)

                results = query.group_by(
                    TheatreMember.name
                ).order_by(
                    func.count(func.distinct(TheatreProcedureRecord.id)).desc()
                ).all()

                items = []
                for team_name, procedures, avg_duration in results:
                    # Get delay rate and on-time percentage for this team member
                    delay_count_query = session.query(
                        func.count(func.distinct(TheatreProcedureRecord.id))
                    ).select_from(TheatreRecordTeamMember).join(
                        TheatreMember, TheatreMember.id == TheatreRecordTeamMember.theatre_member_id
                    ).join(
                        TheatreProcedureRecord, TheatreProcedureRecord.id == TheatreRecordTeamMember.record_id
                    ).filter(
                        TheatreProcedureRecord.deleted_at.is_(None),
                        TheatreRecordTeamMember.deleted_at.is_(None),
                        TheatreRecordTeamMember.role == TeamRoleEnum.SURGEON,
                        TheatreMember.name == team_name,
                        TheatreProcedureRecord.had_delay.is_(True),
                    )

                    delay_count_query = _apply_date_range_filter(delay_count_query, date_range)

                    if theatre_unit_uid:
                        delay_count_query = delay_count_query.join(
                            TheatreUnit, TheatreUnit.id == TheatreProcedureRecord.theatre_unit_id
                        ).filter(TheatreUnit.uid == theatre_unit_uid)

                    delay_count = delay_count_query.scalar() or 0

                    delay_rate = round((delay_count / procedures) * 100, 1) if procedures > 0 else 0.0
                    on_time_pct = round(100.0 - delay_rate, 1)

                    items.append(TeamPerformanceItemNode(
                        team=team_name,
                        procedures=procedures,
                        avg_duration=round(float(avg_duration), 1),
                        delay_rate=delay_rate,
                        on_time_pct=on_time_pct,
                    ))

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Team performance retrieved successfully",
                    data=TeamPerformanceListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve team performance",
                    data=None,
                )

    @staticmethod
    def get_procedures_heatmap(
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[ProceduresHeatmapListNode]:
        """Get procedure density by day of week and hour slot."""
        with session_scope() as session:
            try:
                # Use PostgreSQL EXTRACT for day of week (0=Sunday, 1=Monday, ...)
                # We'll map to hour slots based on start time
                query = session.query(
                    func.extract('dow', TheatreProcedureRecord.procedure_date).label("day_of_week"),
                    TheatreProcedureRecord.procedure_start_time,
                    func.count(TheatreProcedureRecord.id).label("count"),
                ).filter(
                    TheatreProcedureRecord.deleted_at.is_(None),
                )

                query = _apply_date_range_filter(query, date_range)

                if theatre_unit_uid:
                    query = query.join(TheatreUnit).filter(TheatreUnit.uid == theatre_unit_uid)

                results = query.group_by(
                    func.extract('dow', TheatreProcedureRecord.procedure_date),
                    TheatreProcedureRecord.procedure_start_time,
                ).order_by(
                    func.extract('dow', TheatreProcedureRecord.procedure_date).asc(),
                    TheatreProcedureRecord.procedure_start_time.asc(),
                ).all()

                # Map day_of_week (0=Sunday) to day name
                day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

                # Aggregate into hour slots
                slot_map = {}
                for day_of_week, start_time, count in results:
                    # Convert start_time to hour slot
                    hour = start_time.hour
                    if hour < 8:
                        continue  # Before 8 AM
                    elif hour < 10:
                        slot = "08:00–10:00"
                    elif hour < 12:
                        slot = "10:00–12:00"
                    elif hour < 14:
                        slot = "12:00–14:00"
                    elif hour < 16:
                        slot = "14:00–16:00"
                    elif hour < 18:
                        slot = "16:00–18:00"
                    else:
                        continue  # After 6 PM

                    day_name = day_names[int(day_of_week)]
                    key = (day_name, slot)
                    slot_map[key] = slot_map.get(key, 0) + count

                items = []
                for day_name in DAY_ORDER:
                    for slot in HOUR_SLOTS:
                        count = slot_map.get((day_name, slot), 0)
                        if count > 0:
                            items.append(ProceduresHeatmapItemNode(
                                day=day_name,
                                hour=slot,
                                count=count,
                            ))

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Procedures heatmap retrieved successfully",
                    data=ProceduresHeatmapListNode(items=items),
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve procedures heatmap",
                    data=None,
                )


AnalyticsCrud = AnalyticsService