from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import CourseAssessment
from src.models.student import Student
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAssessmentInput, CourseAssessmentNode


class CourseAssessmentService(object):
    @staticmethod
    def get_course_assessment() -> List[CourseAssessment]:
        with session_scope() as session:
            result = session.query(CourseAssessment).filter(CourseAssessment.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_course_assessment_by_id(id: List[int]) -> List[CourseAssessment]:
        """
        Get Course Assessment by code
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseAssessment).where(
                (CourseAssessment.id.in_(id)) & (CourseAssessment.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_assessment_by_uids(uids: List[str]) -> List[CourseAssessment]:
        """
        Get Course Assessment by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseAssessment).where(
                (CourseAssessment.uid.in_(uids)) & (CourseAssessment.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_assessment_by_uid(uid: str) -> CourseAssessment:
        """
        Get Course Assessment by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseAssessment).where(
                (CourseAssessment.uid == uid) & (CourseAssessment.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_course_assessment(self, inputs: List[CourseAssessmentInput]) -> Response[List[CourseAssessmentNode]]:
        """
        Register Course Assessment
        :param inputs:
        :return:
        """
        course_assessment_list = []
        with session_scope() as session:
            # Check if the course assessment already exist using uid
            existed_course_assessment_list = self.get_course_assessment_by_id(
                [course_assessment.id for course_assessment in inputs if course_assessment.uid is None])
            if existed_course_assessment_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_course_assessment_list,
                                message="Course Assessment Already Exists")
            # check for existing course using uid
            existed_course_assessment = self.get_course_assessment_by_id([inputItem.id for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    course_assessment = CourseAssessment(
                        program_course_id=inputItem.program_course_id,
                        exam_category_uid=inputItem.exam_category_uid,
                        minimum_exams=inputItem.minimum_exams,
                        can_exceed_minimum=inputItem.can_exceed_minimum,
                        maximum_score=inputItem.maximum_score
                    )
                    course_assessment_list.append(course_assessment)
                else:
                    course_assessment = next(
                        filter(lambda course_assessment: str(course_assessment.uid) == str(inputItem.uid),
                               existed_course_assessment), None)
                    if course_assessment:
                        course_assessment.program_course_id = inputItem.program_course_id,
                        course_assessment.exam_category_uid = inputItem.exam_category_uid,
                        course_assessment.minimum_exams = inputItem.minimum_exams,
                        course_assessment.can_exceed_minimum = inputItem.can_exceed_minimum,
                        course_assessment.maximum_score = inputItem.maximum_score
                        course_assessment_list.append(course_assessment)
            session.add_all(course_assessment_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=course_assessment_list,
                            message="Successfully Submitted Course Assessment")

    # Delete Function
    @staticmethod
    def remove_course_assessment(uid: str):
        """
        Remove Course Assessment by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(CourseAssessment).filter_by(uid=uid).update({CourseAssessment.deleted_at: pendulum.now()})
            session.commit()
