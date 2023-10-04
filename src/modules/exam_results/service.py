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
    def get_student_exam_results(student_uid) -> List[ExamResult]:
        with session_scope() as session:

            result = session.query(ExamResult).filter(ExamResult.student_uid == student_uid,ExamResult.deleted_at.is_(None)).all()
            return result





