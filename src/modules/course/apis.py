# Importing useful libraries
from typing import List

import strawberry #For building graphQL APIs

from src.models import Course
from src.modules.course.service import CourseService, CourseCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, CourseNode, PaginationInput, PaginatedCourse


@strawberry.type
class CourseQuery:
    @strawberry.field
    def get_courses(self, pagination: PaginationInput) -> Response[PaginatedCourse]:
        try:
            result = CourseCrud.get_multi_paginated(pagination, ['name', 'code', 'description', 'exam_category_uid', 'can_exceed_minimum_by', ''], PaginatedCourse)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Courses Retrieved Successfully",
            data=result)

    @strawberry.field
    def get_course(self, uid: str) -> Response[CourseNode | None]:
        try:
            result = CourseService.get_course_by_uid(uid)
        except Exception as e:
            print(e)
            result = []

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course not found",
                data=None)


@strawberry.type
class CourseMutation:
    @strawberry.field
    def register_courses(self, inputs: List[CourseInput]) -> Response[PaginatedCourse]:
        try:
            return CourseService(Course).register_courses(inputs)

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Register Course", data=[])

    @strawberry.mutation
    async def remove_course(self, uid: str) -> Response[None]:
        """
        Remove Course By UID
        :param uid:
        :return:
        """
        try:
            CourseService(Course).remove_course(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Course",
                data=None
            )
