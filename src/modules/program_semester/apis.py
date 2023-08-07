from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import ProgramSemester
from src.modules.program_semester.service import ProgramSemesterService, ProgramSemesterCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterNode, ProgramSemesterInput, PaginationInput, ProgramSemesterListNode


@strawberry.type
class ProgramSemesterQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_SEMESTERS"])])
    def get_program_semesters(self, pagination: PaginationInput) -> Response[Optional[ProgramSemesterListNode]]:
        try:
            result = ProgramSemesterCrud.get_multi_paginated(pagination, ['study_year', 'semester', 'core_credits', 'elective_credits'], ProgramSemesterListNode, ['program', 'academic_year'])
        except Exception as e:
            print(e)
            result = ProgramSemesterListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Program Semesters",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_SEMESTERS"])])
    def get_program_semester(self, uid: str) -> Response[ProgramSemesterNode | None]:
        try:
            result = ProgramSemesterService.get_program_semester_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Semester retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program Semester not found",
                data=None)


@strawberry.type
class ProgramSemesterMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROGRAM_SEMESTERS"])])
    def register_program_semester(self, inputs: List[ProgramSemesterInput]) -> Response[Optional[ProgramSemesterListNode]]:
        try:
            return ProgramSemesterService(ProgramSemester).register_program_semesters(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Register Program Semester",
                            data=ProgramSemesterListNode(items=[], total_count=0),)

    # Delete programs type function
    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_PROGRAM_SEMESTERS"])])
    async def remove_program_semester(self, uid: str) -> Response[None]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            ProgramSemesterService(ProgramSemester).remove_program_semester(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Semester Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Program Semester",
                data=None
            )
