from typing import List

import strawberry

from src.modules.course.service import CourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, CourseNode

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
            message="Students retrieved successfully",
            data=result)

@strawberry.type
class CourseMutation:
    @strawberry.field
    def register_courses(self, inputs: List[CourseInput]) -> Response[List[CourseNode]]:
        try:
            return CourseService().register_courses(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register course", data=[])
