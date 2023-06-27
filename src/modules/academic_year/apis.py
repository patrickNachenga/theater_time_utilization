from typing import List

import strawberry

from src.models import AcademicYear
from src.modules.academic_year.service import AcademicYearService, AcademicYearCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import AcademicYearInput, PaginationInput, AcademicYearListNode, AcademicYearNode


@strawberry.type
class AcademicYearQuery:
    @strawberry.field
    def get_academic_years(self, pagination: PaginationInput) -> Response[AcademicYearListNode]:
        try:
            result = AcademicYearCrud.get_multi_paginated(pagination, ['name', 'status', 'start_date', 'end_date'],
                                                          AcademicYearListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Academic Year retrieved successfully",
            data=result)

    @strawberry.field
    def get_academic_year(self, uid: str) -> Response[AcademicYearNode | None]:
        try:
            result = AcademicYearService.get_academic_year_by_uid(uid)
        except Exception as e:
            print(e)
            result = []

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Academic Year retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Academic year not found",
                data=None)

    @strawberry.field
    def get_academic_year(self) -> Response[AcademicYearNode | None]:
        try:
            result = AcademicYearService.get_active_academic_year()
        except Exception as e:
            print(e)
            result = []

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Active Academic Year retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Active Academic year not found",
                data=None)


@strawberry.type
class AcademicYearMutation:
    @strawberry.field
    def register_academic_year(self, inputs: List[AcademicYearInput]) -> Response[AcademicYearListNode]:
        try:
            return AcademicYearService(AcademicYear).register_academic_year(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Add Academic Year",
                            data=AcademicYearListNode(items=[], total_count=0))

    @strawberry.mutation
    async def remove_academic_year(self, uid: str) -> Response[None]:
        """
        Remove Academic Year By UID
        :param uid:
        :return:
        """
        try:
            AcademicYearService(AcademicYear).remove_academic_year(uid)
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
