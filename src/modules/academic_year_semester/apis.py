from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models.academic_year_semester import AcademicYearSemester
from src.modules.academic_year_semester.service import AcademicYearSemesterCrud, AcademicYearSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput, \
    AcademicYearSemesterListNode, AcademicYearSemesterInput, AcademicYearSemesterNode


@strawberry.type
class AcademicYearSemesterQuery:

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_ACADEMIC_YEAR_SEMESTERS"])])
    def get_academic_year_semesters(self, pagination: PaginationInput) -> Response[Optional[AcademicYearSemesterListNode]]:
        try:
            result = AcademicYearSemesterCrud.get_multi_paginated(pagination,
                                                                  ["oddStartDate", "oddEndDate", "evenStartDate",
                                                                   "evenStartDate"
                                                                   "examStartDate", "examTicketDate"],
                                                                  AcademicYearSemesterListNode, ['academic_year'])
        except Exception as e:
            print(e)
            result = AcademicYearSemesterListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Academic Year Semester Retrieved successfully",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_ACADEMIC_YEAR_SEMESTERS"])])
    def get_academic_year_semester(self, uid: str) -> Response[Optional[AcademicYearSemesterNode]]:
        try:
            result = AcademicYearSemesterService.get_academic_year_semesters_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieve Academic Year Semester",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Academic Year Semester not found",
                data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_ACADEMIC_YEAR_SEMESTER"])])
    def get_academic_year_semester_by_academic_year(self, academic_year_uid: str) -> Response[Optional[List[AcademicYearSemesterNode]]]:
        try:
            return AcademicYearSemesterService.get_academic_year_semesters_by_academic_year(academic_year_uid)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Failed to Retrieve Academic Year Semester",
                data=[])


@strawberry.type
class AcademicYearSemesterMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_ACADEMIC_YEAR_SEMESTER"])])
    def register_academic_year_semester(self, inputs: List[AcademicYearSemesterInput]) -> Response[AcademicYearSemesterListNode]:
        try:
            return AcademicYearSemesterService(AcademicYearSemester).register_academic_semesters(inputs)

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Academic Year Semester",
                            data=AcademicYearSemesterListNode(items=[], total_count=0), )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_ACADEMIC_YEAR_SEMESTER"])])
    async def remove_academic_year_semester(self, uid: str) -> Response[None]:
        """
        Remove academic year semester
        :param uid:
        :return:
        """
        try:
            result = AcademicYearSemesterService(AcademicYearSemester).remove_academic_year_semester(uid)
            print(result)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Academic Year Semester Removed Successful",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Academic Year Semester",
                data=None
            )
