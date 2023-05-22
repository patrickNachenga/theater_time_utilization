from typing import List

import strawberry

from src.modules.program.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramNode, ProgramInput


@strawberry.type
class ProgramQuery:
    @strawberry.field
    def get_programs(self) -> Response[List[ProgramNode]]:
        try:
            result = ProgramService.get_programs()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Program retrieved successfully",
            data=result)


@strawberry.type
class ProgramMutation:
    @strawberry.field
    def register_program(self, inputs: List[ProgramInput]) -> Response[List[ProgramNode]]:
        try:
            return ProgramService().register_get_program(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register program", data=[])

    # delete program
    @strawberry.mutation
    async def remove_program(self, uid: str) -> Response[None]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            ProgramService.remove_program(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Program",
                data=None
            )
