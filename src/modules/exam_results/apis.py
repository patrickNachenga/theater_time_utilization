import logging
from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.modules.exam_results.service import ExamResultService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultNode, ExcelFile

logger = logging.getLogger(__name__)


@strawberry.type
class ExamResultQuery:
    @strawberry.field()  # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])]
    def get_exam_results(self) -> Response[List[ExamResultNode]]:
        try:
            result = ExamResultService.get_exam_results()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Results Retrieved Successfully",
                data=result,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve exam result summaries: {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve exam result summaries",
                data=[],
            )

    @strawberry.field()  # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])]
    def generate_partial_transcript(self, registration_number: str, info: Info) -> Response[ExcelFile]:
        try:
            return ExamResultService.generate_partial_transcript(registration_number, info)
        except Exception as e:
            logger.error(f"Failed to retrieve : {e}")
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve course results",
                data=ExcelFile(base64_data=[], file_name=""),
            )

    @strawberry.field()  # extensions=[CustomPermissionExtension(["VIEW_EXAM_RESULTS"])]
    def get_student_exam_results(self, student_uid: str) -> \
            Response[List[ExamResultNode]]:
        try:
            result = ExamResultService.get_student_exam_results(student_uid)

            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Results Retrieved Successfully",
                data=result
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve exam result summaries",
                data=[]
            )


@strawberry.type
class ExamResultMutation:
    @strawberry.mutation(extensions=[CustomPermissionExtension(["PUBLISH_EXAM_RESULTS"])])
    def publish_exam_result_by_program_semester_uid(self, program_semester_uids: List[str], info: Info) -> Response[None]:
        try:
            return ExamResultService.publish_exam_result(program_semester_uids, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Publish Exam Results",
                data=None
            )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["PUBLISH_EXAM_RESULTS"])])
    def publish_all_exam_results(self, academic_year_uid: str, semester: int, info: Info) -> Response[None]:
        try:
            return ExamResultService.publish_all_exam_results(academic_year_uid,semester, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Publish Exam Results",
                data=None
            )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["UN_PUBLISH_EXAM_RESULTS"])])
    def un_publish_all_semester_exam_result(self, academic_year_uid: str, semester: int, info: Info) -> Response[None]:
        try:
            return ExamResultService.un_publish_all_semester_exam_result(academic_year_uid, semester, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Unpublish Exam Results",
                data=None
            )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["UN_PUBLISH_EXAM_RESULTS"])])
    def un_publish_semester_exam_result_by_program_semester_uids(self, program_semester_uids: List[str], info: Info) -> \
            Response[None]:
        try:
            return ExamResultService.un_publish_semester_exam_result_by_program_semester_uids(program_semester_uids,
                                                                                              info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Unpublish Exam Results",
                data=None
            )
