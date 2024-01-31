# Importing useful libraries
from typing import List, Optional

import strawberry  # For building graphQL APIs

from src.core.security import CustomPermissionExtension, Info
from src.models import Course
from src.modules.course.service import CourseService, CourseCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, CourseNode, PaginationInput, PaginatedCourse


@strawberry.type
class CourseQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSES"])])
    def get_courses(self, pagination: PaginationInput, info: Info) -> Response[PaginatedCourse]:
        try:
            # result = CourseCrud.get_multi_paginated(pagination, ['name', 'code', 'description'], PaginatedCourse)
            result = CourseCrud.get_multi_paginated(pagination, ['name', 'code', 'description'], PaginatedCourse)
            # result = CourseCrud.get_courses_with_headship(info, pagination, ['name', 'code', 'description'])
        except Exception as e:
            print(e)
            result = PaginatedCourse(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Courses Retrieved Successfully",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSES"])])
    def get_course(self, uid: str) -> Response[CourseNode]:
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
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_COURSES"])])
    async def register_courses(self, inputs: List[CourseInput]) -> Response[PaginatedCourse]:
        try:
            return CourseService(Course).register_courses(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Register Course",
                            data=PaginatedCourse(items=[], total_count=0))

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_COURSE"])])
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
