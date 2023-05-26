from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import ProgramCourseAssessment
from src.models.student import Student
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseAssessmentInput, ProgramCourseAssessmentNode


class ProgramCourseAssessmentService(object):
    @staticmethod
    def get_program_course_assessment() -> List[ProgramCourseAssessment]:
        with session_scope() as session:
            result = session.query(ProgramCourseAssessment).filter(ProgramCourseAssessment.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_course_assessment_by_id(id: List[int]) -> List[ProgramCourseAssessment]:
        """
        Get Course Assessment by code
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourseAssessment).where((ProgramCourseAssessment.id.in_(id)) & (ProgramCourseAssessment.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_course_assessment_by_uids(uids: List[str]) -> List[ProgramCourseAssessment]:
        """
        Get Course Assessment by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourseAssessment).where((ProgramCourseAssessment.uid.in_(uids)) & (ProgramCourseAssessment.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_course_assessment_by_uid(uid: str) -> ProgramCourseAssessment:
        """
        Get Course Assessment by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourseAssessment).where((ProgramCourseAssessment.uid == uid) & (ProgramCourseAssessment.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_program_course_assessment(self, inputs: List[ProgramCourseAssessmentInput]) -> Response[List[ProgramCourseAssessmentNode]]:
        """
        Register Course Assessment
        :param inputs:
        :return:
        """
        program_course_assessment_list = []
        with session_scope() as session:
            # Check if the course assessment already exist using uid
            existed_program_course_assessment_list = self.get_program_course_assessment_by_id(
                [program_course_assessment.id for program_course_assessment in inputs if program_course_assessment.uid is None])
            if existed_program_course_assessment_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_course_assessment_list,
                                message="Course Assessment Already Exists")
            # check for existing course using uid
            existed_program_course_assessment = self.get_program_course_assessment_by_id([inputItem.id for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program_course_assessment = ProgramCourseAssessment(
                        program_course_id=inputItem.program_course_id,
                        exam_category_uid=inputItem.exam_category_uid,
                        minimum_exams=inputItem.minimum_exams,
                        can_exceed_minimum_by=inputItem.can_exceed_minimum_by,
                        maximum_score=inputItem.maximum_score
                    )
                    program_course_assessment_list.append(program_course_assessment)
                else:
                    program_course_assessment = next(filter(lambda program_course_assessment: str(program_course_assessment.uid) == str(inputItem.uid),
                                         existed_program_course_assessment), None)
                    if program_course_assessment:
                        program_course_assessment.program_course_id = inputItem.program_course_id,
                        program_course_assessment.exam_category_uid = inputItem.exam_category_uid,
                        program_course_assessment.minimum_exams = inputItem.minimum_exams,
                        program_course_assessment.can_exceed_minimum_by = inputItem.can_exceed_minimum_by,
                        program_course_assessment.maximum_score = inputItem.maximum_score
                        program_course_assessment_list.append(program_course_assessment)
            session.add_all(program_course_assessment_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=program_course_assessment_list,
                            message="Successfully Submitted Course Assessment")

    # Delete Function
    @staticmethod
    def remove_program_course_assessment(uid: str):
        """
        Remove Course Assessment by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ProgramCourseAssessment).filter_by(uid=uid).update({ProgramCourseAssessment.deleted_at: pendulum.now()})
            session.commit()
