from typing import List

import pendulum
from sqlalchemy import select
from src.db.session import session_scope
from src.models import ProgramCourse
from src.modules.course.service import CourseService
from src.modules.course_category.service import CourseCategoryService
from src.modules.program_semester.service import ProgramSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseInput, ProgramCourseNode, ProgramCourseListNode


class ProgramCourseService(object):
    @staticmethod
    def get_program_courses() -> List[ProgramCourse]:
        with session_scope() as session:
            result = session.query(ProgramCourse).filter(ProgramCourse.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_courses_by_ids(ids: List[str]) -> List[ProgramCourse]:
        """
        Get programs Course by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where((ProgramCourse.id.in_(ids)) & (ProgramCourse.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_courses_by_uids(uids: List[str]) -> List[ProgramCourse]:
        """
        Get programs course by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where(
                (ProgramCourse.uid.in_(uids)) & (ProgramCourse.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    def register_program_courses(self, inputs: List[ProgramCourseInput]) -> Response[List[ProgramCourseNode]]:
        """
        Register programs Course
        :param inputs:
        :return Response[List[ProgramCourseNode]]:
        """
        program_course_list = []
        action_type = "Register"
        with session_scope() as session:
            # Check if the program courses already exist using uid
            existed_program_course_list = self.get_program_courses_by_uids(
                [program_course.uid for program_course in inputs if program_course.uid is None])
            if existed_program_course_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_course_list,
                                message="Program Course Already Exists")
            # check for existing programs courses using uid
            existed_program_course = self.get_program_courses_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied Program uid. and get existed program id from returned program model
                try:
                    program_semester_id = ProgramSemesterService.get_program_semester_by_uid(inputItem.program_uid).id
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseListNode(items=[], total_count=0),
                                    message="Please make sure you have submitted correct programs semester value")

                # Verify and get supplied Course uid. and get existed Course id from returned Course model
                try:
                    course_id = CourseService.get_course_by_uid(inputItem.program_uid).id
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseListNode(items=[], total_count=0),
                                    message="Please make sure you have submitted correct courses value")

                # Verify and get supplied Course uid. and get existed Course id from returned Course model
                try:
                    course_category_id = CourseCategoryService.get_course_by_uid(inputItem.program_uid).id
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseListNode(items=[], total_count=0),
                                    message="Please make sure you have submitted correct courses category value")

                if inputItem.uid is None:
                    program_course = ProgramCourse(
                        program_semester_id=program_semester_id,
                        course_id=course_id,
                        credit=inputItem.credit,
                        course_category_id=course_category_id,
                        lecture_hours=inputItem.lecture_hours,
                        seminar_hours=inputItem.seminar_hours,
                        practical_hours=inputItem.practical_hours,
                        assignment_hours=inputItem.assignment_hours,
                        independent_study_hours=inputItem.independent_study_hours,
                        pass_hours=inputItem.pass_hours
                    )
                    program_course_list.append(program_course)
                else:

                    program_course = next(
                        filter(lambda program_course: str(program_course.uid) == str(inputItem.uid),
                               existed_program_course), None)
                    if program_course:
                        program_course.program_semester_id = program_semester_id,
                        program_course.course_id = course_id,
                        program_course.course_category_id = course_category_id,
                        program_course.credit = inputItem.credit,
                        program_course.lecture_hours = inputItem.lecture_hours,
                        program_course.seminar_hours = inputItem.seminar_hours,
                        program_course.practical_hours = inputItem.practical_hours,
                        program_course.assignment_hours = inputItem.assignment_hours,
                        program_course.independent_study_hours = inputItem.independent_study_hours,
                        program_course.pass_hours = inputItem.pass_hours
            session.add_all(program_course_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=program_course_list,
                            message=f"Successfully to {action_type} Program course")

    # Delete FUnction
    @staticmethod
    def remove_program_course(uid: str):
        """
        Remove Program course by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ProgramCourse).filter_by(uid=uid).update({ProgramCourse.deleted_at: pendulum.now()})
            session.commit()
