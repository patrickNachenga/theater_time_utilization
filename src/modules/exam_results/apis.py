import logging
from typing import List

import strawberry

from src.modules.exam_result_summary.service import ExamResultSummaryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultSummaryNode, ExamResultSummaryInput, ExamResultNode

logger = logging.getLogger(__name__)


@strawberry.type
class ExamResultSummaryQuery:
    @strawberry.field
    def get_exam_results(self) -> Response[List[ExamResultNode]]:
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

    @strawberry.field
    def get_exam_results_by_uids(self, uids: List[str]) -> \
            Response[List[ExamResultSummaryNode]]:
        try:
            result = ExamResultSummaryService.get_exam_result_summaries_by_uids(uids)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Results Retrieved Successfully",
                data=result
                )
        except Exception as e:
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve exam result summaries",
                data=[]
            )


@strawberry.type
class ExamResultSummaryMutation:
    @strawberry.field
    def register_exam_results(
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

    @strawberry.field
    def remove_exam_result(self, uid: str) -> Response[None]:
        try:
            ExamResultSummaryService.remove_exam_result_summary(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Result Summary Removed Successfully",
                data=None,
            )
        except Exception as e:
            logger.error(f"Failed to remove exam result summary: {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to remove exam result summary",
                data=None,
            )


schema = strawberry.Schema(query=ExamResultSummaryQuery, mutation=ExamResultSummaryMutation)
