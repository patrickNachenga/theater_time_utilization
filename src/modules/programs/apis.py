from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.models import Program
from src.modules.programs.service import ProgramService, ProgramCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, PaginationInput, ProgramListNode, ProgramNode


@strawberry.type
class ProgramQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAMS"])])
    def get_programs(self, pagination: PaginationInput, info: Info) -> Response[Optional[ProgramListNode]]:
        try:
            # result = ProgramCrud.get_multi_paginated(pagination,
            #                                          ['code', 'short_name', 'tcu_code', 'nacte_code', 'name',
            #                                           'registration_code'], ProgramListNode, ["program_category"])
            result = ProgramCrud.get_programs_with_headship(info, pagination,
                                                     ['code', 'short_name', 'tcu_code', 'nacte_code', 'name',
                                                      'registration_code'], ["program_category"])
        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
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
                data=result)

    @strawberry.field
    def get_program(self, uid: str) -> Response[Optional[ProgramNode]]:
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

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAMS"])])
    def get_programs_by_program_category_uid(self, program_category_uid: str) -> Response[Optional[ProgramListNode]]:
        try:
            result = ProgramService(Program).get_programs_by_category(program_category_uid)
        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
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

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAMS"])])
    def get_programs_by_department_uid(self, department_uid: str) -> Response[Optional[ProgramListNode]]:
        try:
            result = ProgramService(Program).get_programs_by_department(department_uid)
        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
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
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROGRAMS"])])
    def register_program(self, inputs: List[ProgramInput]) -> Response[Optional[ProgramListNode]]:
        try:
            return ProgramService(Program).register_program(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register programs", data=[])

    # delete programs
    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_PROGRAM"])])
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
