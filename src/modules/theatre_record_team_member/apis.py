import strawberry
from typing import List

from src.modules.theatre_record_team_member.service import TheatreRecordTeamMemberService, TheatreRecordTeamMemberCrud
from src.modules.theatre_record_team_member.types import TheatreRecordTeamMemberInput, TheatreRecordTeamMemberListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class TheatreRecordTeamMemberQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_RECORD_TEAM_MEMBERS"])])
    def get_theatre_record_team_members(self, pagination: PaginationInput) -> Response[TheatreRecordTeamMemberListNode]:
        try:
            result = TheatreRecordTeamMemberCrud.get_multi_paginated(pagination, ['record_uid'], TheatreRecordTeamMemberListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordTeamMemberListNode(items=[], total_count=0))


@strawberry.type
class TheatreRecordTeamMemberMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_RECORD_TEAM_MEMBERS"])])
    def register_theatre_record_team_members(self, inputs: List[TheatreRecordTeamMemberInput]) -> Response[TheatreRecordTeamMemberListNode]:
        try:
            return TheatreRecordTeamMemberService(TheatreRecordTeamMemberCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordTeamMemberListNode(items=[], total_count=0))
