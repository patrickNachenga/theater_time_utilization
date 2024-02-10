from typing import List

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import Group
from src.modules.groups.service import GroupService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import GroupNode, GroupInput


@strawberry.type
class GroupQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_GROUPS"])])
    def get_groups(self) -> Response[List[GroupNode]]:
        try:
            result = GroupService.get_groups()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Groups retrieved successfully",
            data=result)

@strawberry.type
class GroupMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_GROUPS"])])
    def register_groups(self, inputs: List[GroupInput]) -> Response[List[GroupNode]]:
        try:
            return GroupService().register_groups(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Groups", data=[])

    # delete Group
    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_GROUP"])])
    async def remove_group(self, uid: str) -> Response[None]:
        """
        Remove Group By UID
        :param uid:
        :return:
        """
        try:
            GroupService.remove_group(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Group Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Group",
                data=None
            )
