from typing import List

from sqlalchemy.orm import Session

from src.db.session import session_scope
from src.models.exam_coursework import ExamCoursework


class ExamCourseworkService:
    def register_exam_coursework(self, exam_coursework: ExamCoursework) -> ExamCoursework:
        with session_scope() as session:
            session.add(exam_coursework)
            session.commit()
            session.refresh(exam_coursework)
            return exam_coursework

    def get_exam_coursework(self, exam_coursework_id: int) -> ExamCoursework:
        with session_scope() as session:
            return session.query(ExamCoursework).get(exam_coursework_id)

    def get_all_exam_courseworks(self) -> List[ExamCoursework]:
        with session_scope() as session:
            return session.query(ExamCoursework).all()

    def update_exam_coursework(self, exam_coursework: ExamCoursework) -> ExamCoursework:
        with session_scope() as session:
            session.add(exam_coursework)
            session.commit()
            session.refresh(exam_coursework)
            return exam_coursework

    def delete_exam_coursework(self, exam_coursework_id: int) -> ExamCoursework:
        with session_scope() as session:
            exam_coursework = session.query(ExamCoursework).get(exam_coursework_id)
            if not exam_coursework:
                raise Exception(f"Exam coursework object not found with ID: {exam_coursework_id}")
            session.delete(exam_coursework)
            session.commit()
            return exam_coursework


exam_coursework_service = ExamCourseworkService()
