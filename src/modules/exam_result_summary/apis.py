import logging
from typing import List

import strawberry

from src.modules.exam_result_summary.service import ExamResultSummaryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultSummaryNode, ExamResultSummaryInput

logger = logging.getLogger(__name__)


@strawberry.type
class ExamResultSummaryQuery:
    @strawberry.field
    def get_exam_result_summaries(self) -> Response[List[ExamResultSummaryNode]]:
        try:
            result = ExamResultSummaryService.get_exam_result_summaries()
            print("Data inserted", result)
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


@strawberry.type
class ExamResultSummaryMutation:
    @strawberry.field
    def register_exam_result_summaries(
            self, inputs: List[ExamResultSummaryInput]
    ) -> Response[List[ExamResultSummaryNode] | None]:
        try:
            result = ExamResultSummaryService().register_exam_result_summaries(inputs)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Result Summaries Registered Successfully",
                data=result,
            )
        except Exception as e:
            logger.error(f"Failed to register exam result summaries: {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to register exam result summaries",
                data=None,
            )


schema = strawberry.Schema(query=ExamResultSummaryQuery, mutation=ExamResultSummaryMutation)
