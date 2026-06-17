import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.dashboard.service import DashboardCrud
from src.modules.dashboard.types import DashboardStatsNode, DelayDistributionListNode, TheatreUnitActivityListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


@strawberry.type
class DashboardQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_dashboard_stats(self) -> Response[DashboardStatsNode]:
        try:
            return DashboardCrud.get_dashboard_stats()
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve dashboard stats",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_delay_distribution(self) -> Response[DelayDistributionListNode]:
        try:
            return DashboardCrud.get_delay_distribution()
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve delay distribution",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_theatre_unit_activity(self) -> Response[TheatreUnitActivityListNode]:
        try:
            return DashboardCrud.get_theatre_unit_activity()
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve theatre unit activity",
                data=None,
            )