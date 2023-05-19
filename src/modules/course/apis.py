from typing import List

import strawberry

from src.modules.course.service import CourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode


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
            message="Successfully Retrieve Students",
            data=result)


@strawberry.type
class StudentMutation:
    @strawberry.field
    def register_students(self, inputs: List[CourseInput]) -> Response[List[CourseNode]]:
        try:
            result = CourseService().register_courses(inputs)
            return Response(status=True, message="Course registered successfully", code=ResponseCode.SUCCESS,
                            data=result)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register course", data=[])
