from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.models import Group
from src.modules.exam_course_result_forwar_logs.service import ExamCourseResultForwardLogService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCourseResultForwardLogNode


@strawberry.type
class ExamCourseResultForwardLogsQuery:
    @strawberry.field()
    # @strawberry.field(extensions=[CustomPermissionExtension(["GET_UPLOAD_RESULT_DEADLINE"])])
    def get_exam_course_result_forward_logs_by_program_course_uid(self, program_course_uid: str, info: Info) -> \
    Response[List[ExamCourseResultForwardLogNode]]:
        try:
            result = ExamCourseResultForwardLogService \
                .get_exam_course_result_forward_logs_by_program_course_uid(program_course_uid, info)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Exam Course Result Logs retrieved successfully",
            data=result)
