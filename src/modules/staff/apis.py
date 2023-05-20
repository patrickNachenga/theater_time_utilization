from typing import List

import strawberry

from src.modules.staff.service import StaffService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StaffNode, StaffInput


@strawberry.type
class StaffQuery:
    @strawberry.field
    def get_staffs(self) -> Response[List[StaffNode]]:
        try:
            result = StaffService.get_staffs()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Staff retrieved successfully",
            data=result)


@strawberry.type
class StaffMutation:
    @strawberry.field
    def register_staff(self, inputs: List[StaffInput]) -> Response[List[StaffNode]]:
        try:
            return StaffService().register_staffs(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register staff", data=[])
