from typing import List

import pendulum
import requests
from sqlalchemy import select

from src.core.config import settings
from src.db.session import session_scope
from src.models import StudentCourseRegistration
from src.models.program_course_student_assessment import ProgramCourseStudentAssessment
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import UploadResultDeadlineNode, StudentCourseAssessmentNode, StudentCourseAssessmentInput


class ProgramCourseStudentAssessmentService(object):
    @staticmethod
    def get_student_program_course_assessment_result(student_course_registration_uid, question_no) -> Response[StudentCourseAssessmentNode]:
        with session_scope() as session:
            # Get student course Registration
            course_registration = session.query(StudentCourseRegistration).filter(
                StudentCourseRegistration.uid == student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).one()
            if not course_registration:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None,
                                message="Student Course Registration is not registered")

            assessment_result = session.query(ProgramCourseStudentAssessment).filter(
                ProgramCourseStudentAssessment.deleted_at.is_(None),
                ProgramCourseStudentAssessment.question_no == question_no,
                ProgramCourseStudentAssessment.student_course_registration_id == course_registration.id).one()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=assessment_result,
                            message="Student Course Registration Assessment Retried Successful")
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
                return Response(status=False, code=ResponseCode.SUCCESS,
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
