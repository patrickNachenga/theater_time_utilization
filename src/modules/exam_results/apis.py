from typing import List

import strawberry

from src.modules.exam_results.service import ExamResultService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultInput, ExamResultNode


@strawberry.type
class ExamResultQuery:
    @strawberry.field
    def get_exam_results(self) -> Response[List[ExamResultNode]]:
        try:
            result = ExamResultService.get_exam_results()
        except Exception as e:
            print(e)

            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Exam Results Retrieved Successfully",
            data=result)

@strawberry.type
class ExamResultMutation:
    @strawberry.field
    def register_exam_results(self, inputs: List[ExamResultInput]) -> Response[List[ExamResultNode]]:
        try:
            result = ExamResultService().register_exam_results(inputs)
            return Response(status=True, message="Record successfully", code=ResponseCode.SUCCESS,
                            data=result)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Exam results", data=[])

