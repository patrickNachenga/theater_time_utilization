import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.analytics.service import AnalyticsCrud
from src.modules.analytics.types import (
    AnalyticsStatsNode,
    ProceduresOverTimeListNode,
    PieChartListNode,
    TheatreUtilizationListNode,
    EstimatedVsActualListNode,
    DelaysOverTimeListNode,
    DurationDistributionListNode,
    ProceduresByRegionListNode,
    TeamPerformanceListNode,
    ProceduresHeatmapListNode,
)
from src.shared.response import Response
from src.shared.response_code import ResponseCode


@strawberry.type
class AnalyticsQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_analytics_stats(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[AnalyticsStatsNode]:
        try:
            return AnalyticsCrud.get_analytics_stats(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve analytics stats",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_procedures_over_time(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
        procedure_uid: str = None,
    ) -> Response[ProceduresOverTimeListNode]:
        try:
            return AnalyticsCrud.get_procedures_over_time(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
                procedure_uid=procedure_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve procedures over time",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_patient_type_distribution(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[PieChartListNode]:
        try:
            return AnalyticsCrud.get_patient_type_distribution(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve patient type distribution",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_patient_outcomes(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[PieChartListNode]:
        try:
            return AnalyticsCrud.get_patient_outcomes(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve patient outcomes",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_theatre_utilization(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[TheatreUtilizationListNode]:
        try:
            return AnalyticsCrud.get_theatre_utilization(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve theatre utilization",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_estimated_vs_actual_duration(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[EstimatedVsActualListNode]:
        try:
            return AnalyticsCrud.get_estimated_vs_actual_duration(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve estimated vs actual duration",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_delays_over_time(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
        procedure_uid: str = None,
    ) -> Response[DelaysOverTimeListNode]:
        try:
            return AnalyticsCrud.get_delays_over_time(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
                procedure_uid=procedure_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve delays over time",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_duration_distribution(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[DurationDistributionListNode]:
        try:
            return AnalyticsCrud.get_duration_distribution(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve duration distribution",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_procedures_by_region(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[ProceduresByRegionListNode]:
        try:
            return AnalyticsCrud.get_procedures_by_region(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve procedures by region",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_team_performance(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[TeamPerformanceListNode]:
        try:
            return AnalyticsCrud.get_team_performance(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve team performance",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_procedures_heatmap(
        self,
        date_range: str = None,
        theatre_unit_uid: str = None,
    ) -> Response[ProceduresHeatmapListNode]:
        try:
            return AnalyticsCrud.get_procedures_heatmap(
                date_range=date_range,
                theatre_unit_uid=theatre_unit_uid,
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve procedures heatmap",
                data=None,
            )