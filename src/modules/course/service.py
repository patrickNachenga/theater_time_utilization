import uuid
from typing import List

import pendulum
import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc, and_, or_, inspect, cast, String
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import Info
from src.db.session import session_scope
from src.helpers.utils import get_user_departments_headship
from src.models import Course, StudentCourseRegistration, ProgramCourse, ProgramSemester, AcademicYear
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseInput, PaginatedCourse, CourseNode, CourseRegistrationNode


class CourseService(CRUDBase[Course, CourseInput, CourseInput]):
    @staticmethod
    def get_courses() -> List[Course]:
        with session_scope() as session:
            result = session.query(Course).filter(Course.deleted_at.is_(None)).order_by(
                desc(Course.updated_at)).all()
            return result

    @staticmethod
    def get_courses_with_headship(info: Info, pagination, search_columns: List[str],
                                  relationships_to_join: List[str] = None,
                                  unique_search: List[dict] = None) -> [PaginatedCourse]:
        """
            Get all programs by program
        :return:
        """
        with session_scope() as session:
            user_h_department_uids = get_user_departments_headship(info)

            query = session.query(Course).filter(
                and_(Course.deleted_at.is_(None), Course.department_uid.in_(user_h_department_uids)))
            search_q = pagination.search if pagination.search else ''

            # filter condition if specified unique column
            unique_filter_conditions = []
            if unique_search:
                for condition in unique_search:
                    for column, value in condition.items():
                        unique_filter_conditions.append(getattr(Course, column) == value)
            if unique_filter_conditions:
                query = query.filter(and_(*unique_filter_conditions))

            # Apply filters
            filter_conditions = []
            for column in inspect(Course).columns:
                if column.name in search_columns:
                    filter_conditions.append(cast(getattr(Course, column.name), String).ilike(f"%{str(search_q)}%"))

            if filter_conditions:
                query = query.filter(or_(*filter_conditions))

            total_count = query.count()

            # Apply pagination
            query = query.limit(pagination.limit).offset(pagination.offset * pagination.limit)
            # Fetch items and total count
            if relationships_to_join and len(relationships_to_join) > 0:
                for relationship_name in relationships_to_join:
                    query = query.options(joinedload(relationship_name))
            items = query.all()
            session.close()

            return PaginatedCourse(items=items, total_count=total_count)

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

    @staticmethod
    def get_unregister_moodle_course() -> Course:
        """
        Get course with null moodle id
        :param:
        :return:
        """
        with session_scope() as session:
            stmt = select(Course).where((Course.moodle_id.is_(None)) & (Course.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_hod_student_course_registration(input) -> List[CourseRegistrationNode]:
        with (session_scope() as session):
            # Get student Uid
            response = requests.get(settings.UAA_URi + f"/users/student-uid-by-registration-number?registration_number={input.registration_number}")
            if response.status_code == 200:
                data = response.json()
                if data["status"] == 200:
                    # Get academic year    id
                    year = session.query(AcademicYear.id).filter(AcademicYear.uid == input.academic_year_uid).first()
                    if year:
                        results = session.query(StudentCourseRegistration). \
                            join(ProgramCourse, ProgramCourse.id == StudentCourseRegistration.program_course_id) . \
                            join(ProgramSemester, ProgramSemester.id == ProgramCourse.program_semester_id). \
                            filter(StudentCourseRegistration.student_uid == data["uid"],
                                   ProgramSemester.study_year == input.study_year,
                                   ProgramSemester.semester == input.semester,
                                   ProgramSemester.academic_year_id == year.id). \
                            order_by(StudentCourseRegistration.core_elective.asc()) .all()
                        if results:
                            for result in results:
                                print(result.uid)

                        return results
            # stmt = select(Course).where((Course.moodle_id.is_(None)) & (Course.deleted_at.is_(None)))
            # result = session.scalars(stmt)
            # return result.first()


    @staticmethod
    def get_register_moodle_course() -> Course:
        """
        Get course with null moodle id
        :param:
        :return:
        """
        with session_scope() as session:
            stmt = select(Course).where((Course.moodle_id.isnot(None)) & (Course.deleted_at.is_(None)))
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
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=PaginatedCourse(items=existed_course_list, total_count=0),
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
            session.commit()
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
