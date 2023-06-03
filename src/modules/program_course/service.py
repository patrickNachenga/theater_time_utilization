from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc
from src.db.session import session_scope
from src.models import ProgramCourse
from src.modules import CRUDBase
from src.modules.course.service import CourseService
from src.modules.course_category.service import CourseCategoryService
from src.modules.program_semester.service import ProgramSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseInput, ProgramCourseListNode


class ProgramCourseService(CRUDBase[ProgramCourse, ProgramCourseInput, ProgramCourseInput]):
    @staticmethod
    def get_program_courses() -> List[ProgramCourse]:
        with session_scope() as session:
            result = session.query(ProgramCourse).filter(ProgramCourse.deleted_at.is_(None)).order_by(
                desc(ProgramCourse.updated_at)).all()
            return result

    @staticmethod
    def get_program_course_by_uid(uid: str) -> ProgramCourse:
        """
        Get Program Course by uid
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where((ProgramCourse.uid == uid) & (ProgramCourse.deleted_at.is_(None))).order_by(
                desc(ProgramCourse.updated_at))
            result = session.scalars(stmt)
            return result.first()

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

    @staticmethod
    def check_uniqueness(course_id: int, program_semester_id: int) -> ProgramCourse:
        """
        Check if there already exists program course with same course_id, program_semester_id all together
        :return ProgramCourse:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where(
                (ProgramCourse.course_id == course_id) &
                (ProgramCourse.program_semester_id == program_semester_id) &
                (ProgramCourse.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    def register_program_courses(self, inputs: List[ProgramCourseInput]) -> Response[ProgramCourseListNode]:
        """
        Register programs Course
        :param inputs:
        :return Response[List[ProgramCourseNode]]:
        """
        program_course_list = []
        action_type = "Register"
        with session_scope() as session:
            # check for existing programs courses using uid
            existed_program_course = self.get_program_courses_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied Program uid. and get existed program model
                program_semester = ProgramSemesterService.get_program_semester_by_uid(
                    inputItem.program_semester_uid)
                if program_semester is None:
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseListNode(items=[], total_count=0),
                                    message="You have submitted incorrect programs semester details")

                # Verify and get supplied Course uid. and get existed Course id from returned Course model
                course = CourseService.get_course_by_uid(inputItem.course_uid)
                if course is None:
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseListNode(items=[], total_count=0),
                                    message="You have submitted incorrect courses details")

                # Verify and get supplied Course category uid. and get existed Course category id from returned Course model
                course_category = CourseCategoryService.get_course_category_by_uid(inputItem.course_category_uid)
                if course_category is None:
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseListNode(items=[], total_count=0),
                                    message="You have submitted incorrect courses category details")

                if inputItem.uid is None:
                    # validate if this program semester is not deprecated
                    deprecated_program_course = self.check_uniqueness(course_id=course.id,
                                                                      program_semester_id=program_semester.id)
                    if deprecated_program_course:
                        return Response(
                            status=False,
                            code=ResponseCode.FAILURE,
                            data=ProgramCourseListNode(items=[], total_count=0),
                            message="Program Course Already Exist"
                        )

                    program_course = ProgramCourse(
                        program_semester=program_semester,
                        course=course,
                        credit=inputItem.credit,
                        course_category=course_category,
                        lecture_hours=inputItem.lecture_hours,
                        seminar_hours=inputItem.seminar_hours,
                        practical_hours=inputItem.practical_hours,
                        assignment_hours=inputItem.assignment_hours,
                        independent_study_hours=inputItem.independent_study_hours,
                        pass_hours=inputItem.pass_hours
                    )
                    local_object = session.merge(program_course)
                    session.add(local_object)
                    session.commit()
                    program_course_list.append(local_object)
                else:
                    action_type = "Update"
                    program_course = next(
                        filter(lambda program_course_data: str(program_course_data.uid) == str(inputItem.uid),
                               existed_program_course), None)
                    if program_course:
                        obj_data = jsonable_encoder(inputItem)
                        # # Replace referenced uids field with model required ids field
                        obj_data['program_semester'] = program_semester
                        obj_data['course'] = course
                        obj_data['course_category'] = course_category
                        for key, value in obj_data.items():
                            setattr(program_course, key, value)

                        local_object = session.merge(program_course)
                        session.add(local_object)
                        session.commit()
                        program_course_list.append(local_object)

            count = session.query(ProgramCourse).filter(ProgramCourse.deleted_at.is_(None)).count()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramCourseListNode(items=program_course_list, total_count=count),
                            message=f"Successfully to {action_type} Program Course")

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


ProgramCourseCrud = ProgramCourseService(ProgramCourse)
