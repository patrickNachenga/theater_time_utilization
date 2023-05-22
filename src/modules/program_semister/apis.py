from typing import List

import strawberry

from src.modules.program_semister.service import ProgramSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterNode, ProgramSemester


@strawberry.type
class ProgramSemesterQuery:
    @strawberry.field
    def get_program_sem_units(self) -> Response[List[ProgramSemesterNode]]:
        try:
            result = ProgramSemesterService.get_program_semester()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Program Sem Unit Retrieved successfully",
            data=result)


@strawberry.type
class ProgramSemUnitMutation:
    @strawberry.field
    def register_staff(self, inputs: List[ProgramSemester]) -> Response[List[ProgramSemesterNode]]:
        try:
            return ProgramSemesterService().register_program_sem_units(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Program Sem Unit Registration Failed", data=[])
