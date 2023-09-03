from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.core.security import Info
from src.models import StudentManuscript
from src.modules.student_manuscript.service import StudentManuscriptService, StudentManuscriptCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentManuscriptInput, StudentManuscriptNode


@strawberry.type
class StudentManuscriptQuery:

    @strawberry.field()
    def get_student_manuscript(self) -> Response[List[StudentManuscriptNode]]:
        try:
            result = StudentManuscriptService(StudentManuscript).get_student_manuscript()
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Manuscript Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Manuscript not found",
                data=None)
    @strawberry.field()
    def get_student_manuscript_by_uid(self, uid: str) -> Response[List[StudentManuscriptNode]]:
        try:
            result = StudentManuscriptService(StudentManuscript).get_student_manuscript_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Manuscript Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Manuscript not found",
                data=None)

    @strawberry.field()
    def get_student_manuscript_by_student_uid(student_uid: str) \
            -> Response[List[StudentManuscriptNode]]:
        try:
            result = StudentManuscriptService.get_student_manuscript_by_student_uid(student_uid)
        except Exception as e:
            print(e)
            result = None

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Manuscript Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Manuscript not found",
                data=None)


@strawberry.type
class StudentManuscriptMutation:
    @strawberry.field()
    def register_student_manuscript(self, inputs: List[StudentManuscriptInput]) \
            -> Response[StudentManuscriptNode]:
        try:
            return StudentManuscriptService(StudentManuscript).register_student_manuscript(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Manuscript not found",
                data=None)

    @strawberry.mutation()
    async def remove_student_manuscript(self, uid: str) -> Response[None]:
        """
        Remove Manuscript by UID
        :param uid:
        :return:
        """
        try:
            StudentManuscriptService.remove_student_manuscript(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Manuscript Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Student Manuscript ",
                data=None
            )
