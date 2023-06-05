import uuid
from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models import Course
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, PaginatedCourse


class CourseService(CRUDBase[Course, CourseInput, CourseInput]):
    @staticmethod
    def get_courses() -> List[Course]:
        with session_scope() as session:
            result = session.query(Course).filter(Course.deleted_at.is_(None)).order_by(
                desc(Course.updated_at)).all()
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
    def get_course_by_uid(uid: str) -> Course | None:
        """
        Get course by uid
        :param uid:
        :return:
        """
        try:
            # Convert the input UID string to a UUID object
            uid_uuid = uuid.UUID(uid)
        except ValueError:
            # Handle the case when the input UID is not a valid UUID
            return None

        with session_scope() as session:
            stmt = select(Course).where((Course.uid == uid_uuid) & (Course.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_courses(self, inputs: List[CourseInput]) -> Response[PaginatedCourse]:
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
                return Response(status=False, code=ResponseCode.DUPLICATE, data=PaginatedCourse(items=existed_course_list, total_count=0),
                                message="Course Already Exists")
            # check for existing course using uid
            existed_course = self.get_courses_by_uids([inputItem.uid for inputItem in inputs])
            action_name = "Register"
            for inputItem in inputs:
                if inputItem.uid is None:
                    course = Course(
                        code=inputItem.code,
                        description=inputItem.description,
                        name=inputItem.name,
                        offered=inputItem.offered,
                        department_uid=inputItem.department_uid
                    )
                    course_list.append(course)
                else:
                    action_name = "Updated"
                    course = next(filter(lambda course: str(course.code) == str(inputItem.code),
                                         existed_course), None)
                    if course:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(course, key, value)
                        course_list.append(course)
            session.add_all(course_list)
            count = session.query(Course).filter(Course.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=PaginatedCourse(items=course_list, total_count=count),
                            message=f"Course {action_name} Successfully")

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


CourseCrud = CourseService(Course)
