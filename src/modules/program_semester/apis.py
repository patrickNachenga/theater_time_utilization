from typing import List

import strawberry

from src.modules.program_semester.service import ProgramSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterNode, ProgramSemesterInput


@strawberry.type
class ProgramSemesterQuery:
    @strawberry.field
    def get_program_semester(self) -> Response[List[ProgramSemesterNode]]:
        try:
            result = ProgramSemesterService.get_program_semesters()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Program Semesters",
            data=result)


@strawberry.type
class ProgramSemesterMutation:
    @strawberry.field
    def register_program_semester(self, inputs: List[ProgramSemesterInput]) -> Response[List[ProgramSemesterNode]]:
        try:
            return ProgramSemesterService().register_program_semesters(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Register Program Semester",
                            data=[])

    # Delete programs type function
    @strawberry.mutation
    async def remove_program_semester(self, uid: str) -> Response[None]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            ProgramSemesterService().remove_program_semester(uid)
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
