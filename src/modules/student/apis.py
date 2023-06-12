from typing import List

import strawberry

from src.models import Program
from src.modules.programs.service import ProgramService, ProgramCrud
from src.modules.student.service import StudentService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, PaginationInput, ProgramListNode, ProgramNode, CourseRegistrationListNode, \
    CourseRegistrationInputNode, UaaDataResponse, StudentUaaData


@strawberry.type
class StudentQuery:
    @strawberry.field
    def get_student_current_course_registration(self, student_uid: str) -> Response[CourseRegistrationListNode]:
        try:
            result = StudentService().get_student_current_course_registration(student_uid)

            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Registration Retrieved successfully",
                data=result)
        except Exception as e:
            print(e)
            result = CourseRegistrationListNode(items=[], total_count=0)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Registration not found",
                data=result)

    @strawberry.field
    def get_allocation_students(self, allocation_uid: str) -> UaaDataResponse:
        try:
            result = StudentService().get_allocation_students(allocation_uid)
            response = UaaDataResponse(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieved",
                data=[StudentUaaData(registration_number=item['registration_number'],full_name=item['full_name']) for item in result['data']]
            )

            return response

        except Exception as e:
            print(e)
            return UaaDataResponse(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Failed to retrieve",
                data=[])


@strawberry.type
class StudentMutation:
    @strawberry.field
    def register_student_course(self, inputs: List[CourseRegistrationInputNode]) -> Response[
        CourseRegistrationListNode]:
        try:
            result = StudentService().register_student_course(inputs)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Registered successfully",
                data=result)
        except Exception as e:
            print(e)
            result = CourseRegistrationListNode(items=[], total_count=0)
        return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register course", data=result)
