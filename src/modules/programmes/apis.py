from typing import List

import strawberry

from src.modules.programmes.service import ProgrammeService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StaffNode, StaffInput, ProgrammeNode, ProgrammeInput


@strawberry.type
class ProgrammeQuery:
    @strawberry.field
    def get_programmes(self) -> Response[List[ProgrammeNode]]:
        try:
            result = ProgrammeService.get_programmes()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Programme retrieved successfully",
            data=result)


@strawberry.type
class ProgrammeMutation:
    @strawberry.field
    def register_programme(self, inputs: List[ProgrammeInput]) -> Response[List[ProgrammeNode]]:
        try:
            return ProgrammeService().register_get_programme(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register programme", data=[])
