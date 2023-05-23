from typing import List

import strawberry

from src.modules.academic_year.service import AcademicYearService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import AcademicYearInput, AcademicYearNode

@strawberry.type
class AcademicYearQuery:
    @strawberry.field
    def get_academic_year(self) -> Response[List[AcademicYearNode]]:
        try:
            result = AcademicYearService.get_academic_year()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Academic Year retrieved successfully",
            data=result)

@strawberry.type
class AcademicYearMutation:
    @strawberry.field
    def register_academic_year(self, inputs: List[AcademicYearInput]) -> Response[List[AcademicYearNode]]:
        try:
            return AcademicYearService().register_academic_year(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Add Academic Year", data=[])
    @strawberry.mutation
    async def remove_academic_year(self, uid: str) -> Response[None]:
        """
        Remove Academic Year By UID
        :param uid:
        :return:
        """
        try:
            AcademicYearService().remove_academic_year(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Academic Year Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Academic Year",
                data=None
            )