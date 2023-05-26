from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import Course
from src.models.student import Student
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, CourseNode


class CourseService(object):
    @staticmethod
    def get_courses() -> List[Course]:
        with session_scope() as session:
            result = session.query(Course).filter(Course.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_courses_by_codes(codes: List[str]) -> List[Course]:
        """
        Get courses by code
        :return:
        """
        with session_scope() as session:
            stmt = select(Course).where((Course.code.in_(codes)) & (Course.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_courses_by_uids(uids: List[str]) -> List[Course]:
        """
        Get courses by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(Course).where((Course.uid.in_(uids)) & (Course.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_by_uid(uid: str) -> Course:
        """
        Get course by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(Student).where((Course.reg_no == uid) & (Course.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_courses(self, inputs: List[CourseInput]) -> Response[List[CourseNode]]:
        """
        Register Course
        :param inputs:
        :return:
        """
        course_list = []
        with session_scope() as session:
            # Check if the course already exist using uid
            existed_course_list = self.get_courses_by_codes(
                [course.code for course in inputs if course.uid is None])
            if existed_course_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_course_list,
                                message="Course Already Exists")
            # check for existing course using uid
            existed_course = self.get_courses_by_codes([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    course = Course(
                        code=inputItem.code,
                        description=inputItem.description,
                        name=inputItem.name,
                        offered=inputItem.offered,
                        department_id=inputItem.department_id
                    )
                    course_list.append(course)
                else:
                    course = next(filter(lambda course: str(course.uid) == str(inputItem.uid),
                                         existed_course), None)
                    if course:
                        course.code = inputItem.code,
                        course.description = inputItem.description,
                        course.name = inputItem.name,
                        course.offered = inputItem.offered,
                        course.department_id = inputItem.department_id
                        course_list.append(course)
            session.add_all(course_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=course_list,
                            message="Successfully Submitted")

    # Delete Function
    @staticmethod
    def remove_course(uid: str):
        """
        Remove course by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(Course).filter_by(uid=uid).update({Course.deleted_at: pendulum.now()})
            session.commit()
