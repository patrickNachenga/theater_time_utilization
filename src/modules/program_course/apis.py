from typing import List

import strawberry

from src.models import ProgramCourse
from src.modules.program_course.service import ProgramCourseService, ProgramCourseCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseNode, ProgramCourseInput, PaginationInput, PaginatedProgramCourse


@strawberry.type
class ProgramCourseQuery:
    @strawberry.field
    def get_program_course(self, pagination: PaginationInput) -> Response[PaginatedProgramCourse]:
        try:
            result = ProgramCourseCrud.get_multi_paginated(pagination, ['name', 'code', 'description'], PaginatedProgramCourse)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Program Courses",
            data=result)


@strawberry.type
class ProgramCourseMutation:
    @strawberry.field
    def register_program_course(self, inputs: List[ProgramCourseInput]) -> Response[List[ProgramCourseNode]]:
        """
            register and update program courses
            :param inputs
            :return:List[ProgramCourseNode]
        """
        try:
            return ProgramCourseService().register_program_courses(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Change Program Courses", data=[])

    # Delete programs type function
    @strawberry.mutation
    async def remove_program_course(self, uid: str) -> Response[None]:
        """
        Remove program course By UID
        :param uid:
        :return:
        """
        try:
            ProgramCourseService(ProgramCourse).remove_program_course(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Course Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Course Program Course",
                data=None
            )
