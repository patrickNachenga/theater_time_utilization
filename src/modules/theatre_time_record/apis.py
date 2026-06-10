import strawberry
from typing import List

from src.modules.theatre_time_record.service import TheatreTimeRecordService, TheatreTimeRecordCrud
from src.modules.theatre_time_record.types import TheatreTimeRecordInput, TheatreTimeRecordListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class TheatreTimeRecordQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_theatre_time_records(self, pagination: PaginationInput) -> Response[TheatreTimeRecordListNode]:
        try:
            result = TheatreTimeRecordCrud.get_multi_paginated(pagination, ['patient_mrn', 'patient_type'], TheatreTimeRecordListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreTimeRecordListNode(items=[], total_count=0))


@strawberry.type
class TheatreTimeRecordMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_TIME_RECORDS"])])
    def register_theatre_time_records(self, inputs: List[TheatreTimeRecordInput]) -> Response[TheatreTimeRecordListNode]:
        try:
            return TheatreTimeRecordService(TheatreTimeRecordCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreTimeRecordListNode(items=[], total_count=0))
