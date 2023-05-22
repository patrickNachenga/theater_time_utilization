from typing import List

import strawberry

from src.modules.exam_cat_groups.service import ExamCatGroupsService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCatGroupsInput, ExamCatGroupsNode


@strawberry.type
class ExamCatGroupsQuery:
    @strawberry.field
    def get_exam_cat_groups(self) -> Response[List[ExamCatGroupsNode]]:
        try:
            result = ExamCatGroupsService.get_exam_cat_groups()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Exam Category Group Category",
            data=result)

@strawberry.type
class ExamCatGroupsMutation:
    @strawberry.field
    def register_exam_cat_groups(self, inputs: List[ExamCatGroupsInput]) -> Response[List[ExamCatGroupsNode]]:
        try:
            return ExamCatGroupsService().register_exam_cat_groups(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Category", data=[])