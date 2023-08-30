from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import StudentSeminar
from src.modules.student_seminar.service import StudentSeminarService, StudentSeminarCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentSeminarInput, StudentSeminarNode, StudentSeminarListNode, PaginationInput


@strawberry.type
class StudentSeminarQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_SEMINAR_TYPES"])])
    def get_student_seminars(self, pagination: PaginationInput) -> Response[StudentSeminarListNode]:
        try:
            result = StudentSeminarCrud.get_multi_paginated(pagination, ["description", "name"],
                                                            StudentSeminarListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Student Seminar Retrieved successfully",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_SEMINAR_TYPES"])])
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


@strawberry.type
class StudentSeminarMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_SEMINAR_TYPES"])])
    def register_student_seminar(self, inputs: List[StudentSeminarInput]) -> Response[StudentSeminarListNode]:
        try:
            return StudentSeminarService(StudentSeminar).register_student_seminar(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Seminar not found",
                data=None)

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_SEMINAR_TYPE"])])
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
