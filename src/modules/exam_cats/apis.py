from typing import List

import strawberry

from src.modules.exam_cats.service import ExamCatsService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCatsInput, ExamCatsNode


@strawberry.type
class ExamCatsQuery:
    @strawberry.field
    def get_exam_cats(self) -> Response[List[ExamCatsNode]]:
        try:
            result = ExamCatsService.get_exam_cats()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Exam Category",
            data=result)

@strawberry.type
class ExamCatsMutation:
    @strawberry.field
    def register_exam_cats(self, inputs: List[ExamCatsInput]) -> Response[List[ExamCatsNode]]:
        try:
            result = ExamCatsService().register_exam_cats(inputs)
            return Response(status=True, message="Record successfully", code=ResponseCode.SUCCESS,
                            data=result)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register exam Category", data=[])