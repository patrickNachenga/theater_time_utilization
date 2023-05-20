from typing import List

import strawberry

from src.modules.groups.service import GroupService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import GroupInput, GroupNode


@strawberry.type
class GroupQuery:
    @strawberry.field
    def get_groups(self) -> Response[List[GroupInput]]:
        try:
            result = GroupService()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Groups",
            data=result)

    # TODO: get_groups by uid


@strawberry.type
class GroupMutation:
    @strawberry.field
    def register_groups(self, inputs: List[GroupInput]) -> Response[List[GroupNode]]:
        try:
            result = GroupService().register_groups(inputs)
            return Response(status=True, message="Groups registration successfully", code=ResponseCode.SUCCESS,
                            data=result)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register groups", data=[])
