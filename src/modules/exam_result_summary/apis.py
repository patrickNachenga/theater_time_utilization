import logging
from typing import List

import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.exam_result_summary.service import ExamResultSummaryService, ExamResultSummaryCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultSummaryNode, ExamResultSummaryInput, PaginationInput, ExamResultSummaryListNode, \
    ExamResultSummarySearchCriteria

logger = logging.getLogger(__name__)


@strawberry.type
class ExamResultSummaryQuery:
    @strawberry.field()  # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULT_SUMMARIES"])]
    def get_exam_result_summaries(self, search_criteria: ExamResultSummarySearchCriteria) -> Response[
        List[ExamResultSummaryNode]]:
        try:
            result = ExamResultSummaryService.get_exam_result_summaries(search_criteria)

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

    @strawberry.field()  # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULT_SUMMARIES"])]
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


@strawberry.type
class ExamResultSummaryMutation:
    @strawberry.field()
    def change_result_stage(self, result_summary_uid: str, stage: str) -> Response[bool]:
        try:

            result = ExamResultSummaryService.change_result_stage(result_summary_uid, stage)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Action Successfully",
                data=result
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Action Failed",
                data=[]
            )

    @strawberry.field()
    def change_program_course_result_stage(self, program_course_id: str, stage: str) -> Response[bool]:
        try:

            result = ExamResultSummaryService.change_program_course_result_stage(program_course_id, stage)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Action Successfully",
                data=result
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Action Failed",
                data=[]
            )
