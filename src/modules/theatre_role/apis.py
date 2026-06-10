import strawberry
from typing import List

from src.modules.theatre_role.service import TheatreRoleService, TheatreRoleCrud
from src.modules.theatre_role.types import TheatreRoleInput, TheatreRoleListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class TheatreRoleQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_ROLES"])])
    def get_theatre_roles(self, pagination: PaginationInput) -> Response[TheatreRoleListNode]:
        try:
            result = TheatreRoleCrud.get_multi_paginated(pagination, ['name', 'description'], TheatreRoleListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRoleListNode(items=[], total_count=0))


@strawberry.type
class TheatreRoleMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_ROLES"])])
    def register_theatre_roles(self, inputs: List[TheatreRoleInput]) -> Response[TheatreRoleListNode]:
        try:
            return TheatreRoleService(TheatreRoleCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRoleListNode(items=[], total_count=0))
