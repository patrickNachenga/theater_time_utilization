from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.exam_category.service import ExamCategoryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCategoryNode, ExamCategoryInput


@strawberry.type
class ExamCategoryQuery:
    @strawberry.field
    def get_exam_categories(self) -> Response[Optional[List[ExamCategoryNode]]]:
        try:
            result = ExamCategoryService.get_exam_categories()
        except Exception as e:
            print(e)
            result = None
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Exam Category retrieved successfully",
            data=result)


@strawberry.type
class ExamCategoryMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_EXAM_CATEGORY"])])
    def register_exam_categories(self, inputs: List[ExamCategoryInput]) -> Response[Optional[List[ExamCategoryNode]]]:
        try:
            return ExamCategoryService().register_exam_categories(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Examination Category",
                            data=[])

    # delete programme
    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_EXAM_CATEGORY"])])
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
