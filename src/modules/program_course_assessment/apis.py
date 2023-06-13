from typing import List

import strawberry

from src.models import ProgramCourseAssessment
from src.modules.program_course_assessment.service import ProgramCourseAssessmentService, ProgramCourseAssessmentCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseAssessmentInput, ProgramCourseAssessmentNode, PaginatedProgramCourseAssessment, \
    PaginationInput, ProgramCourseAssessmentListNode


@strawberry.type
class ProgramCourseAssessmentQuery:
    @strawberry.field
    def get_program_course_assessments(self, pagination: PaginationInput) -> Response[PaginatedProgramCourseAssessment]:
        try:
            result = ProgramCourseAssessmentCrud.get_multi_paginated(pagination, ['minimum_exams'
                                                                                  'can_exceed_minimum_by',
                                                                                  'maximum_score'],
                                                                     PaginatedProgramCourseAssessment,
                                                                     ["program_course", "exam_category"])
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Program Course Assessment retrieved successfully",
            data=result)

    @strawberry.field
    def get_program_course_assessment(self, course_uid: str) -> Response[ProgramCourseAssessmentNode | None]:
        try:
            result = ProgramCourseAssessmentService(ProgramCourseAssessment).get_program_course_assessment_by_uid(
                course_uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieve Program Course Assessment",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program Course Assessment not found",
                data=None)


@strawberry.type
class ProgramCourseAssessmentMutation:
    @strawberry.field
    def register_program_course_assessment(self, inputs: List[ProgramCourseAssessmentInput]) -> Response[
        ProgramCourseAssessmentListNode]:
        try:
            return ProgramCourseAssessmentService(ProgramCourseAssessment).register_program_course_assessment(inputs)

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            data=ProgramCourseAssessmentListNode(items=[], total_count=0),
                            message="Failed to Record Program Course Assessment")

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
