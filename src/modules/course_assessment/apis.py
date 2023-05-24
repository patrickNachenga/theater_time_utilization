from typing import List

import strawberry

from src.modules.course_assessment.service import CourseAssessmentService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAssessmentInput, CourseAssessmentNode

@strawberry.type
class CourseAssessmentQuery:
    @strawberry.field
    def get_course_assessment(self) -> Response[List[CourseAssessmentNode]]:
        try:
            result = CourseAssessmentService.get_course_assessment()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Course Assessment retrieved successfully",
            data=result)

@strawberry.type
class CourseAssessmentMutation:
    @strawberry.field
    def register_course_assessment(self, inputs: List[CourseAssessmentInput]) -> Response[List[CourseAssessmentNode]]:
        try:
            return CourseAssessmentService().register_course_assessment(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Add Course Assessment", data=[])
    @strawberry.mutation
    async def remove_course_assessment(self, uid: str) -> Response[None]:
        """
        Remove Course Assessment By UID
        :param uid:
        :return:
        """
        try:
            CourseAssessmentService().remove_course_assessment(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Assessment Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Course Assessment",
                data=None
            )