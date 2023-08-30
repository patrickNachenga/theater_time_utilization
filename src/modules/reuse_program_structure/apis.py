from typing import List

import strawberry

from src.models import ProgramSemester
from src.modules.reuse_program_structure.service import ProgramStructureService, ProgramSemesterCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterNode, ProgramSemesterInput, ReuseProgramStructureInput, ProgramSemesterListNode


@strawberry.type
class ReuseProgramStructureMutation:
    @strawberry.field
    def reuse_program_structure(self, inputs: List[ReuseProgramStructureInput]) -> Response[ProgramSemesterListNode]:
        try:
            return ProgramStructureService(ProgramSemester).reuse_program_structure(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Register Program Semester",
                            data=ProgramSemesterListNode(items=[], total_count=0),)

