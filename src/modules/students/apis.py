from typing import List

import strawberry

from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentNode, StudentInput
from src.modules.students.service import StudentService


@strawberry.type
class StudentQuery:
    @strawberry.field
    def get_students(self) -> Response[List[StudentNode]]:
        try:
            result = StudentService.get_students()
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
    def register_students(self, inputs: List[StudentInput]) -> Response[List[StudentNode]]:
        try:
            return StudentService().register_students(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register students", data=[])
