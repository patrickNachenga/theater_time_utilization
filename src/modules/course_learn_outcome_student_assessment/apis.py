from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.modules.course_learn_outcome_student_assessment.service import CourseLearnOutcomeStudentAssessmentService
from src.modules.program_course_student_assessment.service import ProgramCourseStudentAssessmentService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentCourseLearningOutcomeAssessmentNode, StudentCourseAssessmentInput, \
    StudentCourseLearningOutcomeAssessmentInput


@strawberry.type
class CourseLearnOutcomeStudentAssessmentQuery:
    @strawberry.field()
    # @strawberry.field(extensions=[CustomPermissionExtension(["GET_UPLOAD_RESULT_DEADLINE"])])
    def get_student_course_learn_outcome_assessment_result(self, student_course_registration_uid: str) \
            -> Response[List[StudentCourseLearningOutcomeAssessmentNode]]:
        try:
            return CourseLearnOutcomeStudentAssessmentService \
                .get_student_course_learn_outcome_assessment_result(student_course_registration_uid)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve student course learn outcome assessment",
                data=None)


@strawberry.type
class CourseLearnOutcomeStudentAssessmentMutation:
    @strawberry.field()
    def register_student_course_learn_outcome_assessment_result(self, inputs: StudentCourseLearningOutcomeAssessmentInput) -> Response[None]:
        try:
            return CourseLearnOutcomeStudentAssessmentService().register_student_course_learn_outcome_assessment_result(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Student Course Learn Outcome Assessment", data=[])


