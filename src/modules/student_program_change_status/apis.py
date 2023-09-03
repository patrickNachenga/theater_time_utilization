from typing import List, Optional

import strawberry

from src.modules.student_program_change_status.service import StudentProgramChangeStatusService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCategoryInput, StudentProgramChangeNode, StudentProgramChangeStatusNode, \
    StudentProgramChangeStatusInput


@strawberry.type
class StudentProgramChangeStatusQuery:
    @strawberry.field
    def get_student_program_changes_status(self) -> Response[List[StudentProgramChangeStatusNode]]:
        try:
            result = StudentProgramChangeStatusService().get_student_program_changes_status()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Student Program Change Status",
            data=result)

    @strawberry.field
    def get_student_program_changes_status_by_uid(self, uid: str) -> Response[StudentProgramChangeStatusNode]:
        try:
            result = StudentProgramChangeStatusService().get_student_program_changes_status_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student Program Change Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Student Program Change not found",
                data=None)


@strawberry.type
class StudentProgramChangeStatusMutation:
    @strawberry.field
    def register_student_program_change(self, inputs: List[StudentProgramChangeStatusInput]) -> Response[List[StudentProgramChangeStatusNode]]:
        try:
            return StudentProgramChangeStatusService().register_student_program_change_status(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            data=[],
                            message="Failed to Student Program Change")

    # Delete programs type function
    @strawberry.mutation
    async def remove_student_program_change(self, uid: str) -> Response[None]:
        """
        Remove Program Category By UID
        :param uid:
        :return:
        """
        try:
            StudentProgramChangeStatusService().remove_student_program_change(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Student_program_change Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Student Program Change ",
                data=None
            )
