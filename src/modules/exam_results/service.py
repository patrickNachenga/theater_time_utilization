from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import ExamResult
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultInput, ExamResultNode


class ExamResultService:
    @staticmethod
    def get_exam_results() -> List[ExamResult]:
        with session_scope() as session:
            result = session.query(ExamResult).filter(ExamResult.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_exam_results_by_uids(uids: List[str]) -> List[ExamResult]:
        with session_scope() as session:
            stmt = select(ExamResult).where((ExamResult.uid.in_(uids)) & (ExamResult.deleted_at.is_(None)))
            result = session.execute(stmt).scalars().all()
            return result

    @staticmethod
    def get_exam_result_by_id(id: int) -> ExamResult:
        with session_scope() as session:
            stmt = select(ExamResult).where((ExamResult.id == id) & (ExamResult.deleted_at.is_(None)))
            result = session.execute(stmt).scalars().first()
            return result

    def register_exam_results(self, inputs: List[ExamResultInput]) -> \
            Response[List[ExamResultNode] | None]:
        exam_result_summaries_list = []

        with session_scope() as session:
            existing_exam_results = self.get_exam_result_by_uids([item.uid for item in inputs])
            if existing_exam_results:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                message="Exam Result Summaries Already Exist", data=None)
            else:
                for item in inputs:
                    exam_result_summary = ExamResult(
                        uid=item.uid,
                        student_uid=item.student_uid,
                        program_course_id=item.program_course_id,
                        exam_category_id=item.exam_category_id,
                        registration_number=item.registration_number,
                        student_name=item.student_name,
                        gender=item.gender,
                        course_code=item.course_code,
                        course_name=item.course_name,
                        credit=item.credit,
                        grade=item.grade,
                        grade_point=item.grade_point,
                        grade_remark=item.grade_remark,
                        publish_status=item.publish_status,
                        publisher=item.publisher
                    )
                    exam_result_summaries_list.append(exam_result_summary)

                session.add_all(exam_result_summaries_list)
                session.commit()

        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Exam Result Successfully Submitted",
            data=exam_result_summaries_list
        )

    @staticmethod
    def remove_exam_result_summary(uid: str):
        with session_scope() as session:
            exam_result_summary = session.query(ExamResult).filter_by(uid=uid).first()
            if exam_result_summary:
                exam_result_summary.deleted_at = pendulum.now()
                session.commit()
            else:
                return Response(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Exam Result Summary Not Found",
                    data=None
                )

