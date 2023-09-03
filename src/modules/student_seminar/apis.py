from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.core.security import Info
from src.models import StudentSeminar
from src.modules.student_seminar.service import StudentSeminarService, StudentSeminarCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentSeminarInput, StudentSeminarNode, StudentSeminarListNode, PaginationInput, \
    StudentSeminarsInputNode, AllStudentSeminarNode, AllStudentSeminarListNode, PaginationSeminarInput


@strawberry.type
class StudentSeminarQuery:

    @strawberry.field()
    def get_all_seminar(self, pagination: PaginationSeminarInput) -> Response[AllStudentSeminarListNode]:
        try:
            result = StudentSeminarService.get_all_student_seminar_paginated(pagination, ["status","description", "name"],
                                                                             AllStudentSeminarNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.NO_RECORD_FOUND,
            message="Seminar No Seminars",
            data=AllStudentSeminarListNode(items=[], total_count=0))

    @strawberry.field()
    def get_seminars(self, pagination: PaginationSeminarInput, info: Info) -> Response[AllStudentSeminarListNode]:
        try:
            result = StudentSeminarCrud.get_all_student_seminar_paginated(info, pagination, ['title', 'description', 'status'])
        except Exception as e:
            print(e)
            result = AllStudentSeminarListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Seminar Retrieved Successfully",
            data=result)

    @strawberry.field()
    def get_all_student_seminars(self) -> Response[List[AllStudentSeminarNode]]:
        try:
            return StudentSeminarService.get_all_student_seminars()
        except Exception as e:
            print(e)
        return Response(
            status=False,
            code=ResponseCode.NO_RECORD_FOUND,
            message="Student Seminar not found",
            data=[])

    @strawberry.field()
    def get_student_seminar(self, uid: str) -> Response[StudentSeminarNode]:
        try:
            result = StudentSeminarService(StudentSeminar).get_student_seminar_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Seminar Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Seminar not found",
                data=None)

    @strawberry.field()
    def get_student_seminars_by_student_uid(self, inputs: StudentSeminarsInputNode) -> Response[
        List[StudentSeminarNode]]:
        # try:
        result = StudentSeminarService.get_student_seminar_by_student_uid(inputs)

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Seminar Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Seminar not found",
                data=None)


@strawberry.type
class StudentSeminarMutation:
    @strawberry.field()
    def register_student_seminar(self, inputs: List[StudentSeminarInput]) -> Response[StudentSeminarNode]:
        try:
            return StudentSeminarService(StudentSeminar).register_student_seminar(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Seminar not found",
                data=None)

    @strawberry.mutation()
    async def remove_student_seminar(self, uid: str) -> Response[None]:
        """
        Remove Seminar Type by UID
        :param uid:
        :return:
        """
        try:
            StudentSeminarService.remove_student_seminar(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Seminar Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Student Seminar ",
                data=None
            )
