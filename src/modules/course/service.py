from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models import Course
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, CourseNode


class CourseService(object):
    @staticmethod
    def get_course() -> List[Course]:
        with session_scope() as session:
            result = session.query(
                Course.id,
                Course.reg_no,
                Course.created_at,
                Course.updated_at,
            ).filter(Course.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_courses_by_ids(ids: List[str]) -> List[Course]:
        """
        Get courses by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(Course).where((Course.id.in_(ids)) & (Course.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_by_id(id: str) -> Course:
        """
        Get User by reg_no
        :param id:
        :return:
        """
        with session_scope() as session:
            stmt = select(Course).where((Course.id == id) & (Course.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_courses(self, inputs: List[CourseInput]) -> Response[List[CourseNode]]:
        """
        Register Students
        :param inputs:
        :return:
        """
        course_list = []
        with session_scope() as session:
            # Check if course already exists using id
            existed_course_list = self.get_courses_by_ids(
                [student.reg_no for student in inputs if student.uid is None])
            if existed_course_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_course_list,
                                message="Student Already exist")

            # create new courses
            for item in inputs:
                course = Course(id=item.id)
                course_list.append(course)

            session.add_all(course_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=course_list,
                            message="Successfully Submitted")
