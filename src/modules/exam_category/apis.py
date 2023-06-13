from typing import List

import strawberry

from src.modules.exam_category.service import ExamCategoryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCategoryNode, ExamCategoryInput


@strawberry.type
class ExamCategoryQuery:
    @strawberry.field
    def get_exam_categories(self) -> Response[List[ExamCategoryNode]]:
        try:
            result = ExamCategoryService.get_exam_categories()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Exam Category retrieved successfully",
            data=result)


@strawberry.type
class ExamCategoryMutation:
    @strawberry.field
    def register_exam_categories(self, inputs: List[ExamCategoryInput]) -> Response[List[ExamCategoryNode]]:
        try:
            return ExamCategoryService().register_exam_categories(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Examination Category",
                            data=[])

    # delete programme
    @strawberry.mutation
    async def remove_exam_categories(self, uid: str) -> Response[None]:
        """
        Remove Exam Category By UID
        :param uid:
        :return:
        """
        try:
            ExamCategoryService.remove_exam_categories(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Category Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Exam Category",
                data=None
            )
