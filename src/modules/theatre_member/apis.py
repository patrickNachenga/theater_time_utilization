import strawberry
from typing import List

from src.modules.theatre_member.service import TheatreMemberService, TheatreMemberCrud
from src.modules.theatre_member.types import TheatreMemberInput, TheatreMemberListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class TheatreMemberQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_MEMBERS"])])
    def get_theatre_members(self, pagination: PaginationInput) -> Response[TheatreMemberListNode]:
        try:
            result = TheatreMemberCrud.get_multi_paginated(pagination, ['first_name', 'last_name', 'pf_number'], TheatreMemberListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))


@strawberry.type
class TheatreMemberMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_MEMBERS"])])
    def register_theatre_members(self, inputs: List[TheatreMemberInput]) -> Response[TheatreMemberListNode]:
        try:
            return TheatreMemberService(TheatreMemberCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))
