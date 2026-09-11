import strawberry
from typing import List

from src.models import TheatreMemberRole
from src.modules.theatre_member_role.service import TheatreMemberRoleService, TheatreMemberRoleCrud
from src.modules.theatre_member_role.types import TheatreMemberRoleInput, TheatreMemberRoleListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode

from src.core.security import CustomPermissionExtension, Info


@strawberry.type
class TheatreMemberRoleQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_MEMBER_ROLES"])])
    def get_theatre_member_roles(self, pagination: PaginationInput) -> Response[TheatreMemberRoleListNode]:
        try:
            result = TheatreMemberRoleCrud.get_multi_paginated(
                pagination,
                [],
                TheatreMemberRoleListNode,
                relationships_to_join=[TheatreMemberRole.theatre_member],
            )
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberRoleListNode(items=[], total_count=0))


@strawberry.type
class TheatreMemberRoleMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_MEMBER_ROLES"])])
    def register_theatre_member_roles(self, inputs: List[TheatreMemberRoleInput], info: Info) -> Response[TheatreMemberRoleListNode]:
        try:
            return TheatreMemberRoleService(TheatreMemberRoleCrud.model).register(inputs, info=info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberRoleListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_MEMBER_ROLES"])])
    def remove_theatre_member_role(self, uid: str, info: Info) -> Response[TheatreMemberRoleListNode]:
        try:
            TheatreMemberRoleCrud.remove(uid, info=info)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Role removed successfully",
                            data=TheatreMemberRoleListNode(items=[], total_count=0))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to remove role",
                            data=TheatreMemberRoleListNode(items=[], total_count=0))
