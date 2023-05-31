from typing import List

import strawberry

from src.modules.program_course_assessment.service import ProgramCourseAssessmentService, ProgramCourseAssessmentCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseAssessmentInput, ProgramCourseAssessmentNode, PaginatedProgramCourseAssessment, \
    PaginationInput


@strawberry.type
class ProgramCourseAssessmentQuery:
    @strawberry.field
    def get_program_course_assessment(self, pagination: PaginationInput) -> Response[PaginatedProgramCourseAssessment]:
        try:
            result = ProgramCourseAssessmentCrud.get_multi_paginated(pagination, ['program_course_id', 'program_course', 'minimum_exams', 'maximum_score' ], PaginatedProgramCourseAssessment)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Program Course Assessment retrieved successfully",
            data=result)


@strawberry.type
class ProgramCourseAssessmentMutation:
    @strawberry.field
    def register_program_course_assessment(self, inputs: List[ProgramCourseAssessmentInput]) -> Response[List[ProgramCourseAssessmentNode]]:
        try:
            return ProgramCourseAssessmentService().register_program_course_assessment(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE,
                            message="Failed to Record Program Course Assessment", data=[])

    @strawberry.mutation
    async def remove_program_course_assessment(self, uid: str) -> Response[None]:
        """
        Remove Program Course Assessment By UID
        :param uid:
        :return:
        """
        try:
            ProgramCourseAssessmentService.remove_program_course_assessment(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="program course assessment Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove program course assessment",
                data=None
            )
