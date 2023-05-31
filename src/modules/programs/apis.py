from typing import List

import strawberry

from src.models import Program
from src.modules.programs.service import ProgramService, ProgramCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, PaginationInput, ProgramListNode, ProgramNode


@strawberry.type
class ProgramQuery:
    @strawberry.field
    def get_programs(self, pagination: PaginationInput) -> Response[ProgramListNode]:
        try:
            result = ProgramCrud.get_multi_paginated(pagination, ['name', 'short_name'], ProgramListNode)
        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
        return Response(
            status=False,
            code=ResponseCode.FAILURE,
            message="Program retrieved successfully",
            data=result)

    @strawberry.field
    def get_program(self, uid: str) -> Response[ProgramNode | None]:
        try:
            result = ProgramService.get_program_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program not found",
                data=None)


@strawberry.type
class ProgramMutation:
    @strawberry.field
    def register_program(self, inputs: List[ProgramInput]) -> Response[ProgramListNode]:
        try:
            return ProgramService(Program).register_program(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register programs", data=[])

    # delete programs
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
