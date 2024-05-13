from typing import List

import pendulum
import requests
from sqlalchemy import select

from src.core.config import settings
from src.db.session import session_scope
from src.helpers.utils import qn5_student_program_course_assessment
from src.models import StudentCourseRegistration
from src.models.program_course_student_assessment import ProgramCourseStudentAssessment
from src.models.teaching_and_continuous_course_assessment_result import TeachingAndContinuousCourseAssessmentResult
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import UploadResultDeadlineNode, StudentCourseAssessmentNode, StudentCourseAssessmentInput, \
    StudentTeachingContinuousCourseAssessmentNode, StudentAssessmentNode


class ProgramCourseStudentAssessmentService(object):
    @staticmethod
    def get_student_program_course_assessment_result(student_course_registration_uid, question_no) -> Response[
        StudentCourseAssessmentNode]:
        with session_scope() as session:
            # Get student course Registration
            course_registration = session.query(StudentCourseRegistration).filter(
                StudentCourseRegistration.uid == student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).all()
            if not course_registration:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None,
                                message="Student Course Registration is not registered")
            course_registration = course_registration[0]
            assessment_result = session.query(ProgramCourseStudentAssessment).filter(
                ProgramCourseStudentAssessment.deleted_at.is_(None),
                ProgramCourseStudentAssessment.question_no == question_no,
                ProgramCourseStudentAssessment.student_course_registration_id == course_registration.id).all()
            if assessment_result:
                result = assessment_result[0]
            else:
                result = None

            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=result,
                            message="Student Course Registration Assessment Retried Successful")

    @staticmethod
    def get_student_program_course_assessment_qn5_result(student_course_registration_uid) \
            -> Response[List[StudentAssessmentNode]]:
        with session_scope() as session:
            # Get student course Registration
            course_registration = session.query(StudentCourseRegistration).filter(
                StudentCourseRegistration.uid == student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).one()
            if not course_registration:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None,
                                message="Student Course Registration is not registered")

            # Get All Teaching and continuous assessment
            qns = qn5_student_program_course_assessment()
            return_results = []
            if qns:
                for qn in qns:
                    # Get student teaching and continuous assessment answer
                    assessment_result = session.query(TeachingAndContinuousCourseAssessmentResult).filter(
                        TeachingAndContinuousCourseAssessmentResult.deleted_at.is_(None),
                        TeachingAndContinuousCourseAssessmentResult.assessment_id == qn['id'],
                        TeachingAndContinuousCourseAssessmentResult.student_course_registration_id == course_registration.id).all()
                    if assessment_result:
                        assessment = assessment_result[0]
                        return_results.append(
                            StudentAssessmentNode(
                                uid=assessment.uid,
                                has_answer=True,
                                item_id=qn['id'],
                                item=qn['item'],
                                type=qn['type'],
                                answer=assessment.answer
                            )
                        )
                    else:
                        return_results.append(
                            StudentAssessmentNode(
                                uid=None,
                                has_answer=False,
                                item_id=qn['id'],
                                item=qn['item'],
                                type=qn['type'],
                                answer=None
                            )
                        )
                    # print(assessment.course_learn_outcome.learning_outcome)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=return_results,
                            message="Student Course Assessment Retried Successful")

    @staticmethod
    def register_student_program_course_assessment_result(inputs: StudentCourseAssessmentInput) -> Response[None]:
        with session_scope() as session:
            course_registration = session.query(StudentCourseRegistration).filter(
                StudentCourseRegistration.uid == inputs.student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).all()
            if len(course_registration) == 0:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None,
                                message="Student Course Registration is not registered")
            course_registration = course_registration[0]
            assessment_result = session.query(ProgramCourseStudentAssessment).filter(
                ProgramCourseStudentAssessment.deleted_at.is_(None),
                ProgramCourseStudentAssessment.question_no == inputs.question_no,
                ProgramCourseStudentAssessment.student_course_registration_id == course_registration.id).all()
            if assessment_result:
                assessment_result = assessment_result[0]
                session.query(ProgramCourseStudentAssessment).filter_by(id=assessment_result.id).update(
                    {"answer": inputs.answer}
                )
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=None,
                                message="Successful Student Course Registration Assessment Updated")
            else:
                register = ProgramCourseStudentAssessment(
                    answer=inputs.answer,
                    question_no=inputs.question_no,
                    student_course_registration_id=course_registration.id
                )
                session.add(register)

            session.commit()
            return Response(status=False, code=ResponseCode.SUCCESS,
                            data=None,
                            message="Successful Student Course Registration Assessment Added")
