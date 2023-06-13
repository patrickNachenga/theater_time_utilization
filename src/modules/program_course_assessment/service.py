from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models import ProgramCourseAssessment
from src.modules import CRUDBase
from src.modules.exam_category.service import ExamCategoryService
from src.modules.program_course.service import ProgramCourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseAssessmentInput, ProgramCourseAssessmentListNode


class ProgramCourseAssessmentService(
    CRUDBase[ProgramCourseAssessment, ProgramCourseAssessmentInput, ProgramCourseAssessmentInput]):
    @staticmethod
    def get_program_course_assessment() -> List[ProgramCourseAssessment]:
        with session_scope() as session:
            result = session.query(ProgramCourseAssessment).filter(
                ProgramCourseAssessment.deleted_at.is_(None)).order_by(
                desc(ProgramCourseAssessment.updated_at)).all()
            return result

    @staticmethod
    def get_program_course_assessment_by_id(id: List[int]) -> List[ProgramCourseAssessment]:
        """
        Get Course Assessment by code
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourseAssessment).where(
                (ProgramCourseAssessment.id.in_(id)) & (ProgramCourseAssessment.deleted_at.is_(None))).order_by(
                desc(ProgramCourseAssessment.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_course_assessment_by_uids(uids: List[str]) -> List[ProgramCourseAssessment]:
        """
        Get Course Assessment by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourseAssessment).where(
                (ProgramCourseAssessment.uid.in_(uids)) & (ProgramCourseAssessment.deleted_at.is_(None))).order_by(
                desc(ProgramCourseAssessment.updated_at))
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
            stmt = select(ProgramCourseAssessment).where(
                (ProgramCourseAssessment.uid == uid) & ProgramCourseAssessment.deleted_at.is_(None))
            result = session.scalars(stmt)
            return result.first()

    def register_program_course_assessment(self, inputs: List[ProgramCourseAssessmentInput]) -> Response[
        ProgramCourseAssessmentListNode]:
        """
        Register Program Course Assessment
        :param inputs:
        :return Response[ProgramCourseAssessmentListNode]:
        """
        program_course_assessment_list = []
        action_type = "Register"
        with session_scope() as session:
            # check for existing course using uid
            existed_program_course_assessment = self.get_program_course_assessment_by_uids(
                [inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied Program course uid. and get existed program course id from returned program model
                try:
                    program_course = ProgramCourseService.get_program_course_by_uid(inputItem.program_course_uid)
                    if program_course is None:
                        raise ValueError("You have submitted incorrect programs course details")
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseAssessmentListNode(items=[], total_count=0),
                                    message="You have submitted incorrect programs course details")

                # Verify and get supplied Exam category and get existed  model
                try:
                    exam_category = ExamCategoryService.get_exam_categories_by_uid(inputItem.exam_category_uid)
                    if exam_category is None:
                        raise ValueError("You have submitted incorrect exam category details")
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramCourseAssessmentListNode(items=[], total_count=0),
                                    message="You have submitted incorrect exam category details")
                if inputItem.uid is None:
                    program_course_assessment = ProgramCourseAssessment(
                        program_course=program_course,
                        exam_category=exam_category,
                        minimum_exams=inputItem.minimum_exams,
                        can_exceed_minimum_by=inputItem.can_exceed_minimum_by,
                        maximum_score=inputItem.maximum_score
                    )
                    local_object = session.merge(program_course_assessment)
                    session.add(local_object)
                    session.commit()
                    program_course_assessment_list.append(local_object)
                else:
                    action_type = "Update"
                    program_course_assessment = next(filter(
                        lambda course_assessment: str(course_assessment.uid) == str(inputItem.uid),
                        existed_program_course_assessment), None)
                    if program_course_assessment:
                        obj_data = jsonable_encoder(inputItem)
                        # # Replace referenced uids field with model required ids field
                        obj_data['program_course'] = program_course
                        obj_data['exam_category'] = exam_category

                        for key, value in obj_data.items():
                            setattr(program_course_assessment, key, value)
                        local_object = session.merge(program_course_assessment)
                        session.add(local_object)
                        session.commit()
                        program_course_assessment_list.append(local_object)
                    program_course_assessment_list.append(program_course_assessment)
            session.add_all(program_course_assessment_list)
            count = session.query(ProgramCourseAssessment).filter(ProgramCourseAssessment.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramCourseAssessmentListNode(items=program_course_assessment_list,
                                                                 total_count=count),
                            message=f"Successfully to {action_type} Program Course")

    # Delete Function
    @staticmethod
    def remove_program_course_assessment(uid: str):
        """
        Remove Course Assessment by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ProgramCourseAssessment).filter_by(uid=uid).update(
                {ProgramCourseAssessment.deleted_at: pendulum.now()})
            session.commit()


ProgramCourseAssessmentCrud = ProgramCourseAssessmentService(ProgramCourseAssessment)
