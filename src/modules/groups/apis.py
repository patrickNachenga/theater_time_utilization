from typing import List

import strawberry

from src.models import Group
from src.modules.groups.service import GroupService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, CourseNode, GroupNode, GroupInput


@strawberry.type
class GroupQuery:
    @strawberry.field
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
    @strawberry.field
    def register_groups(self, inputs: List[GroupInput]) -> Response[List[GroupNode]]:
        try:
            return GroupService().register_groups(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Groups", data=[])
