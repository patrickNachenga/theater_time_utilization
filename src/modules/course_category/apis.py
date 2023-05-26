from typing import List

import strawberry

from src.modules.course_category.service import CourseCategoryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseCategoryInput, CourseCategoryNode


@strawberry.type
class CourseCategoryQuery:
    @strawberry.field
    def get_course_categories(self) -> Response[List[CourseCategoryNode]]:
        try:
            result = CourseCategoryService.get_course_categories()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Course Category Retrieved successfully",
            data=result)

@strawberry.type
class CourseCategoryMutation:
    @strawberry.field
    def register_course_categories(self, inputs: List[CourseCategoryInput]) -> Response[List[CourseCategoryNode]]:
        try:
            return CourseCategoryService().register_course_categories(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Register Course C  ategory", data=[])

    @strawberry.mutation
    async def remove_course_category(self, uid: str) -> Response[None]:
        """
        Remove course category by UID
        :param uid:
        :return:
        """
        try:
            result = CourseCategoryService().remove_course_category(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Category Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Course Category",
                data=None
            )
