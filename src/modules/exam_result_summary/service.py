from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import ExamResultSummary
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultSummaryInput, ExamResultSummaryNode


class ExamResultSummaryService:
    @staticmethod
    def get_exam_result_summaries() -> List[ExamResultSummary]:
        with session_scope() as session:
            result = session.query(ExamResultSummary).filter(ExamResultSummary.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_student_exam_result_summaries(student_uid: str) -> List[ExamResultSummary]:
        with session_scope() as session:
            result = session.query(ExamResultSummary).filter(ExamResultSummary.student_uid == student_uid,ExamResultSummary.deleted_at.is_(None)).all()
            return result



