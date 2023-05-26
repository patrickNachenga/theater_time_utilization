# Importing useful libraries
from typing import List

import strawberry #For building graphQL APIs

from src.modules.course.service import CourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, CourseNode

#
@strawberry.type
class CourseQuery:
    @strawberry.field
    def get_courses(self) -> Response[List[CourseNode]]:
        try:
            result = CourseService.get_courses()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Courses Retrieved Successfully",
            data=result)


@strawberry.type
class CourseMutation:
    @strawberry.field
    def register_courses(self, inputs: List[CourseInput]) -> Response[List[CourseNode]]:
        try:
            return CourseService().register_courses(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Register Course", data=[])

    @strawberry.mutation
    async def remove_course(self, uid: str) -> Response[None]:
        """
        Remove Course By UID
        :param uid:
        :return:
        """
        try:
            CourseService().remove_course(uid)
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
