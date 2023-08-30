import logging
from typing import List

import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.exam_results.service import ExamResultService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultNode, ExamResultInput

logger = logging.getLogger(__name__)


@strawberry.type
class ExamResultQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])])
    def get_exam_results(self) -> Response[List[ExamResultNode]]:
        try:
            result = ExamResultService.get_exam_results()
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

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])])
    def get_exam_results_by_uids(self, uids: List[str]) -> \
            Response[List[ExamResultNode]]:
        try:
            result = ExamResultService.get_exam_results_by_uids(uids)
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
class ExamResultMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_EXAM_RESULTS"])])
    def register_exam_results(self, inputs: List[ExamResultInput]) -> \
            Response[List[ExamResultNode]]:
        try:
            result = ExamResultService().get_exam_results()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Results Registered Successfully",
                data=result,
            )
        except Exception as e:
            logger.error(f"Failed to register exam results: {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to register exam results",
                data=None,
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["REMOVE_EXAM_RESULT"])])
    def remove_exam_result(self, uid: str) -> Response[None]:
        try:
            ExamResultService.remove_exam_result_summary(uid)
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
