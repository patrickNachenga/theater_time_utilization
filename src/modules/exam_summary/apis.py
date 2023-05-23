from typing import List

import strawberry

from src.modules.exam_summary.service import ExamSummaryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamSummaryInput, ExamSummaryNode


@strawberry.type
class ExamSummaryQuery:
    @strawberry.field
    def get_exam_summary(self) -> Response[List[ExamSummaryNode]]:
        try:
            result = ExamSummaryService.get_exam_summary()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Exam Results Summary",
            data=result)

@strawberry.type
class ExamSummaryMutation:
    @strawberry.field
    def register_exam_summary(self, inputs: List[ExamSummaryInput]) -> Response[List[ExamSummaryNode]]:
        try:
            result = ExamSummaryService().register_exam_summary(inputs)
            return Response(status=True, message="Record successfully", code=ResponseCode.SUCCESS,
                            data=result)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Record Exam Summary", data=[])