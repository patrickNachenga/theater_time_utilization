from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.modules.program_course_student_assessment.service import ProgramCourseStudentAssessmentService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentCourseAssessmentNode, StudentCourseAssessmentInput, StudentAssessmentNode


@strawberry.type
class ProgramCourseStudentAssessmentQuery:
    @strawberry.field()
    # @strawberry.field(extensions=[CustomPermissionExtension(["GET_UPLOAD_RESULT_DEADLINE"])])
    def get_student_program_course_assessment_result(self, student_course_registration_uid: str, question_no: int,  info: Info) -> Response[StudentCourseAssessmentNode]:
        try:
            if question_no != 5:
                return ProgramCourseStudentAssessmentService \
                    .get_student_program_course_assessment_result(student_course_registration_uid, question_no)
        except Exception as e:
            print(e)
        return Response(
            status=False,
            code=ResponseCode.FAILURE,
            message="Failed to retrieve student program course assessment",
            data=None)

    @strawberry.field()
    # @strawberry.field(extensions=[CustomPermissionExtension(["GET_UPLOAD_RESULT_DEADLINE"])])
    def get_student_program_course_assessment_qn5_result(self, student_course_registration_uid: str, question_no: int,
                                                     info: Info) -> Response[List[StudentAssessmentNode]]:
        try:
            if question_no == 5:
                return ProgramCourseStudentAssessmentService \
                    .get_student_program_course_assessment_qn5_result(student_course_registration_uid)
        except Exception as e:
            print(e)
        return Response(
            status=False,
            code=ResponseCode.FAILURE,
            message="Failed to retrieve student program course assessment",
            data=None)
@strawberry.type
class ProgramCourseStudentAssessmentMutation:
    @strawberry.field()
    def register_student_program_course_assessment_result(self, inputs: StudentCourseAssessmentInput) -> Response[None]:
        try:
            return ProgramCourseStudentAssessmentService().register_student_program_course_assessment_result(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Student Program Course Assessment", data=[])

#     @strawberry.field(extensions=[CustomPermissionExtension(["REMOVE_UPLOAD_RESULT_DEADLINE"])])
#     async def remove_upload_result_deadline(self, uid: str) -> Response[None]:
#         """
#         Remove Course By UID
#         :param uid:
#         :return:
#         """
#         try:
#             UploadResultDeadlineService.remove_upload_result_deadline(uid)
#             return Response(
#                 status=True,
#                 code=ResponseCode.SUCCESS,
#                 message="Upload Result Deadline Removed Successfully",
#                 data=None
#             )
#         except Exception as e:
#             print(e)
#             return Response(
#                 status=False,
#                 code=ResponseCode.FAILURE,
#                 message="Upload Result Deadline to Remove Course",
#                 data=None
#             )
