import strawberry
from typing import List

from sqlalchemy.orm import selectinload

from src.models import TheatreProcedureRecord, TheatreRecordTeamMember
from src.modules.theatre_procedure_record.service import TheatreTimeRecordService, TheatreTimeRecordCrud
from src.modules.theatre_procedure_record.types import TheatreProcedureRecordInput, TheatreTimeRecordListNode, \
    TheatreProcedureRecordNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode

from src.core.security import CustomPermissionExtension


@strawberry.type
class TheatreTimeRecordQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    def get_theatre_time_records(self, pagination: PaginationInput) -> Response[TheatreTimeRecordListNode]:
        try:
            result = TheatreTimeRecordCrud.get_multi_paginated(
                pagination=pagination,
                search_columns=['patient_mrn', 'patient_type'],
                search_node=TheatreTimeRecordListNode,
                relationships_to_join=[
                    TheatreProcedureRecord.patient_region,
                    TheatreProcedureRecord.procedure,
                    TheatreProcedureRecord.theatre_unit,
                ]

                # chain_relationship=[
                #     selectinload(TheatreProcedureRecord.team_members)
                #     .joinedload(TheatreRecordTeamMember.theatre_member)
                # ]
            )
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed",
                            data=TheatreTimeRecordListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_RECORDS"])])
    async def get_theatre_time_record_by_uid(self, uid: str) -> Response[TheatreProcedureRecordNode]:
        return await TheatreTimeRecordService(TheatreTimeRecordCrud.model).get_by_uid(uid)


@strawberry.type
class TheatreTimeRecordMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_TIME_RECORDS"])])
    def register_theatre_time_records(self, inputs: TheatreProcedureRecordInput) -> Response[TheatreTimeRecordListNode]:
        try:
            return TheatreTimeRecordService(TheatreTimeRecordCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed",
                            data=TheatreTimeRecordListNode(items=[], total_count=0))
