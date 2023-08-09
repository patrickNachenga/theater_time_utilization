from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import ProgramCourseAssessment
from src.modules.program_course_assessment.service import ProgramCourseAssessmentService, ProgramCourseAssessmentCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseAssessmentInput, ProgramCourseAssessmentNode, PaginationInput, \
    ProgramCourseAssessmentListNode


@strawberry.type
class ProgramCourseAssessmentQuery:
    # (extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSE_ASSESSMENTS"])])
    @strawberry.field
    def get_program_course_assessments(self, pagination: PaginationInput) -> Response[
        Optional[ProgramCourseAssessmentListNode]]:
        try:
            result = ProgramCourseAssessmentCrud.get_multi_paginated(pagination, ['minimum_exams'
                                                                                  'can_exceed_minimum_by',
                                                                                  'maximum_score'],
                                                                     ProgramCourseAssessmentListNode,
                                                                     ["program_course", "exam_category"])
        except Exception as e:
            print(e)
            result = None
        return Response(
            status=True,
            code=ResponseCode.SUCCESS if result else ResponseCode.NO_RECORD_FOUND,
            message="Program Course Assessment retrieved successfully",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSE_ASSESSMENTS"])])
    def get_program_course_assessment(self, program_course_assessment_uid: str) -> Response[
        Optional[ProgramCourseAssessmentNode]]:
        try:
            result = ProgramCourseAssessmentService(ProgramCourseAssessment).get_program_course_assessment_by_uid(
                program_course_assessment_uid)
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

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSE_ASSESSMENTS"])])
    async def get_program_course_assessment_by_program_course_uid(self, program_course_uid: str) -> Response[
        Optional[ProgramCourseAssessmentListNode]]:
        try:
            program_course_assessment = ProgramCourseAssessmentService.get_program_course_assessment_by_program_course_uid(
                program_course_uid)
            if program_course_assessment:
                return program_course_assessment
            raise ValueError("Unable to retrieve program course assessment")
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                data=ProgramCourseAssessmentListNode(items=None, total_count=0),
                message="Unable to retrieve program course assessment"
            )


@strawberry.type
class ProgramCourseAssessmentMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROGRAM_COURSE_ASSESSMENTS"])])
    def register_program_course_assessment(self, inputs: List[ProgramCourseAssessmentInput]) -> Response[
        Optional[ProgramCourseAssessmentListNode]]:
        try:
            return ProgramCourseAssessmentService(ProgramCourseAssessment).register_program_course_assessment(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            data=ProgramCourseAssessmentListNode(items=[], total_count=0),
                            message="Failed to Record Program Course Assessment")

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_PROGRAM_COURSE_ASSESSMENT"])])
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
