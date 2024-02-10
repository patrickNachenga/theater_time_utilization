import logging
from typing import List

import strawberry

from src.modules.exam_coursework.service import ExamCourseworkService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCourseWorkNode, StudentCourseWorkOutput, StudentCourseWorkInput

logger = logging.getLogger(__name__)


@strawberry.type
class ExamCourseWorkResultQuery:
    @strawberry.field() # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])]
    def get_exam_course_work_results(self) -> Response[List[ExamCourseWorkNode]]:
        try:
            result = ExamCourseworkService.get_exam_course_work_results()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam course work Results Retrieved Successfully",
                data=result,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve exam result summaries: {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve exam course work result summaries",
                data=[],
            )

    @strawberry.field() # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])]
    def get_student_active_semester_course_work_results(self, input: StudentCourseWorkInput) -> Response[List[StudentCourseWorkOutput]]:
        try:
            result = ExamCourseworkService.get_student_active_semester_course_work_results(input)
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve exam result summaries: {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve exam course work result summaries",
                data=[],
            )

    @strawberry.field() # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])]
    def get_student_exam_course_work_results(self, student_uid: str) -> \
            Response[List[ExamCourseWorkNode]]:
        try:
            result = ExamCourseworkService.get_student_exam_course_work_results(student_uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Results Retrieved Successfully",
                data=result
                )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve exam result summaries",
                data=[]
            )


