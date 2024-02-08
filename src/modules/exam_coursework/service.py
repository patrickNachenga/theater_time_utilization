from typing import List

from src.db.session import session_scope
from src.models.exam_coursework import ExamCoursework
from src.models.program_course import ProgramCourse
from src.models.course import Course
from src.models.program_semester import ProgramSemester


class ExamCourseworkService:

    @staticmethod
    def get_exam_course_work_results() -> List[ExamCoursework]:
        with session_scope() as session:
            result = session.query(ExamCoursework).filter(ExamCoursework.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_student_exam_course_work_results(student_uid) -> List[ExamCoursework]:
        with session_scope() as session:
            result = session.query(ExamCoursework) \
                .join(ProgramCourse) \
                .join(ProgramSemester) \
                .join(Course) \
                .filter(ExamCoursework.student_uid == student_uid,
                                                      ExamCoursework.deleted_at.is_(None)).all()
            return result


exam_coursework_service = ExamCourseworkService()
