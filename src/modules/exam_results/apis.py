from typing import List

import strawberry

from src.modules.exam_results.service import ExamResultsService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultsInput, ExamResultsNode


@strawberry.type
class ExamResultsQuery:
    @strawberry.field
    def get_exam_results(self) -> Response[List[ExamResultsNode]]:
        try:
            result = ExamResultsService.get_exam_results()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Exam Category",
            data=result)

@strawberry.type
class ExamResultsMutation:
    @strawberry.field
    def register_exam_results(self, inputs: List[ExamResultsInput]) -> Response[List[ExamResultsNode]]:
        try:
            result = ExamResultsService().register_exam_results(inputs)
            return Response(status=True, message="Record successfully", code=ResponseCode.SUCCESS,
                            data=result)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Exam results", data=[])

