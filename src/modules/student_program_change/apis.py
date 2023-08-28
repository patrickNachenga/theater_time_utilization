from typing import List, Optional

import strawberry

from src.core.security import  LoginRequiredExtension
from src.models import StudentProgramChange
from src.modules.student_program_change.service import StudentProgramChangeService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentProgramChangeInput, StudentProgramChangeNode


@strawberry.type
class StudentProgramChangeCourseQuery:
    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_all_student_change_programs(self) -> Response[List[StudentProgramChangeNode]]:
        try:
            result = StudentProgramChangeService.get_all_student_change_programs()
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

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_student_change_program_by_uid(self, uid: str) -> Response[StudentProgramChangeNode]:
        try:
            result = StudentProgramChangeService.get_student_change_program_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Change Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Requested Program Change Found",
                data=None)


@strawberry.type
class StudentProgramChangeMutation:
    # (extensions=[CustomPermissionExtension(["REGISTER_PROGRAM_CHANGE"])])
    @strawberry.field(extensions=[LoginRequiredExtension()])
    def student_request_change_program(self, input: StudentProgramChangeInput) -> Response[StudentProgramChangeNode]:
        """
            register and update student program change
            :param input
            :return:Response[Optional[StudentProgramChangeNode]]
        """
        try:
            return StudentProgramChangeService(StudentProgramChange).student_change_program(input)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Change Program",
                            data=None, )
