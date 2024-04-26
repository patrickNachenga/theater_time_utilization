from typing import List

from src.db.session import session_scope
from src.models import ProgramCourse
from src.models.exam_course_result_forward_logs import ExamCourseResultForwardLogs
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCourseResultForwardLogNode


class ExamCourseResultForwardLogService(object):
    @staticmethod
    def get_exam_course_result_forward_logs_by_program_course_uid(program_course_uid, info)\
            -> List[ExamCourseResultForwardLogNode]:
        with session_scope() as session:
            results = session.query(ExamCourseResultForwardLogs).join(ProgramCourse) \
                .filter(ProgramCourse.uid.in_([program_course_uid]),
                        ExamCourseResultForwardLogs.deleted_at.is_(None),
                        ExamCourseResultForwardLogs.deleted_at.is_(None)) \
                .order_by(ExamCourseResultForwardLogs.id.asc()) .all()
            return_results = []
            if results:
                status_mapping = {
                    0: "Instructor",
                    1: "HOD",
                    2: "Principal",
                    3: "Provisional Results",
                    4: "Published"
                }
                for result in results:
                    # Map forwarded_from
                    if result.forwarded_from in status_mapping:
                        forwarded_from = status_mapping[result.forwarded_from]
                    else:
                        forwarded_from = "Unknown"  # Handle unknown status
                    # Map forwarded_to
                    if result.forwarded_to in status_mapping:
                        forwarded_to = status_mapping[result.forwarded_to]
                    else:
                        forwarded_to = "Unknown"  # Handle unknown status

                    return_results.append(ExamCourseResultForwardLogNode(
                        program_course=result.program_course,
                        staff_uid=result.staff_uid,
                        staff_name=result.staff_name,
                        forwarded_from=forwarded_from,
                        forwarded_to=forwarded_to,
                        uid=result.uid
                    ))
            return return_results
