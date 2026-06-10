import strawberry
from typing import List

from src.modules.theatre_record_delay.service import TheatreRecordDelayService, TheatreRecordDelayCrud
from src.modules.theatre_record_delay.types import TheatreRecordDelayInput, TheatreRecordDelayListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class TheatreRecordDelayQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_RECORD_DELAYS"])])
    def get_theatre_record_delays(self, pagination: PaginationInput) -> Response[TheatreRecordDelayListNode]:
        try:
            result = TheatreRecordDelayCrud.get_multi_paginated(pagination, ['description'], TheatreRecordDelayListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordDelayListNode(items=[], total_count=0))


@strawberry.type
class TheatreRecordDelayMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_RECORD_DELAYS"])])
    def register_theatre_record_delays(self, inputs: List[TheatreRecordDelayInput]) -> Response[TheatreRecordDelayListNode]:
        try:
            return TheatreRecordDelayService(TheatreRecordDelayCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordDelayListNode(items=[], total_count=0))
