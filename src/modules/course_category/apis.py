from typing import List

import strawberry

from src.models import CourseCategory
from src.modules.course_category.service import CourseCategoryService, CourseCategoryCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseCategoryInput, CourseCategoryNode, CourseCategoryListNode, PaginationInput


@strawberry.type
class CourseCategoryQuery:
    @strawberry.field
    def get_course_categories(self, pagination: PaginationInput) -> Response[CourseCategoryListNode]:
        try:
            result = CourseCategoryCrud.get_multi_paginated(pagination, ['program_courses', 'code', 'description'],
                                                            CourseCategoryListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Course Category Retrieved successfully",
            data=result)

    @strawberry.field
    def get_course_category(self, uid: str) -> Response[CourseCategoryNode | None]:
        try:
            result = CourseCategoryService(CourseCategory).get_course_category_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Category Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Category not found",
                data=None)


@strawberry.type
class CourseCategoryMutation:
    @strawberry.field
    def register_course_categories(self, inputs: List[CourseCategoryInput]) -> Response[CourseCategoryListNode]:
        try:
            return CourseCategoryService(CourseCategory).register_course_categories(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Category not found",
                data=None)

    @strawberry.mutation
    async def remove_course_category(self, uid: str) -> Response[None]:
        """
        Remove course category by UID
        :param uid:
        :return:
        """
        try:
            CourseCategoryService.remove_course_category(uid)
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
