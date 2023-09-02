import logging
from typing import List

import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.exam_result_summary.service import ExamResultSummaryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultSummaryNode, ExamResultSummaryInput

logger = logging.getLogger(__name__)


@strawberry.type
class ExamResultSummaryQuery:
    @strawberry.field() # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULT_SUMMARIES"])]
    def get_exam_result_summaries(self) -> Response[List[ExamResultSummaryNode]]:
        try:
            result = ExamResultSummaryService.get_exam_result_summaries()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Results Retrieved Successfully",
                data=result,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve exam result summaries: {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve exam result summaries",
                data=[],
            )

    @strawberry.field() # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULT_SUMMARIES"])]
    def get_student_exam_result_summaries(self, student_uid: str) -> \
            Response[List[ExamResultSummaryNode]]:
        try:
            result = ExamResultSummaryService.get_student_exam_result_summaries(student_uid)
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


