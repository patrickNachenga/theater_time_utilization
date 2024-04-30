from typing import List

import pendulum
import requests
from sqlalchemy import select

from src.core.config import settings
from src.db.session import session_scope
from src.helpers.utils import teaching_and_continuous_course_assessment
from src.models import StudentCourseRegistration, CourseLearnOutcome, ProgramCourse, Course
from src.models.course_learn_outcome_student_assessment import CourseLearnOutcomeStudentAssessments
from src.models.program_course_student_assessment import ProgramCourseStudentAssessment
from src.models.teaching_and_continuous_course_assessment_result import TeachingAndContinuousCourseAssessmentResult
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentCourseAssessmentInput, StudentCourseLearningOutcomeAssessmentNode, \
    StudentCourseLearningOutcomeAssessmentInput, StudentTeachingContinuousCourseAssessmentNode, \
    TeachingContinuousCourseAssessmentInput


class CourseLearnOutcomeStudentAssessmentService(object):
    @staticmethod
    def get_student_course_learn_outcome_assessment_result(student_course_registration_uid) \
            -> Response[List[StudentCourseLearningOutcomeAssessmentNode]]:
        with session_scope() as session:
            # Get student course Registration
            course_registration = session.query(StudentCourseRegistration).join(ProgramCourse).filter(
                StudentCourseRegistration.uid == student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).one()
            if not course_registration:
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=None,
                                message="Student Course Registration is not registered")

            # Get All Course Leaning Outcome
            course_lean_outcome = session.query(CourseLearnOutcome).filter(
                CourseLearnOutcome.deleted_at.is_(None),
                CourseLearnOutcome.course_id == course_registration.program_course.course_id).all()
            return_results = []
            if course_lean_outcome:
                for learn_outcome in course_lean_outcome:
                    assessment_result = session.query(CourseLearnOutcomeStudentAssessments).filter(
                        CourseLearnOutcomeStudentAssessments.deleted_at.is_(None),
                        CourseLearnOutcomeStudentAssessments.course_learn_outcome_id == learn_outcome.id,
                        CourseLearnOutcomeStudentAssessments.student_course_registration_id == course_registration.id).all()
                    if assessment_result:
                        assessment = assessment_result[0]
                        return_results.append(
                            StudentCourseLearningOutcomeAssessmentNode(
                                uid=assessment.uid,
                                has_answer=True,
                                course_lean_outcome_uid=learn_outcome.uid,
                                course_lean_outcome=learn_outcome.learning_outcome,
                                answer=assessment.answer
                            )
                        )
                    else:
                        return_results.append(
                            StudentCourseLearningOutcomeAssessmentNode(
                                uid=None,
                                has_answer=False,
                                course_lean_outcome_uid=learn_outcome.uid,
                                course_lean_outcome=learn_outcome.learning_outcome,
                                answer=None
                            )
                        )
                    # print(assessment.course_learn_outcome.learning_outcome)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=return_results,
                            message="Student Course Leaning Outcome Assessment Retried Successful")

    @staticmethod
    def get_teaching_and_continuous_course_assessment(student_course_registration_uid) \
            -> Response[List[StudentTeachingContinuousCourseAssessmentNode]]:
        with session_scope() as session:
            # Get student course Registration
            course_registration = session.query(StudentCourseRegistration).join(ProgramCourse).filter(
                StudentCourseRegistration.uid == student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).one()
            if not course_registration:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None,
                                message="Student Course Registration is not registered")

            # Get All Teaching and continuous assessment
            teaching_continuous_assessment = teaching_and_continuous_course_assessment()
            return_results = []
            if teaching_continuous_assessment:
                for tca in teaching_continuous_assessment:
                    # Get student teaching and continuous assessment answer
                    assessment_result = session.query(TeachingAndContinuousCourseAssessmentResult).filter(
                        TeachingAndContinuousCourseAssessmentResult.deleted_at.is_(None),
                        TeachingAndContinuousCourseAssessmentResult.assessment_id == tca['id'],
                        TeachingAndContinuousCourseAssessmentResult.student_course_registration_id == course_registration.id).all()
                    if assessment_result:
                        assessment = assessment_result[0]
                        return_results.append(
                            StudentTeachingContinuousCourseAssessmentNode(
                                uid=assessment.uid,
                                has_answer=True,
                                assessment_id=tca['id'],
                                assessment=tca['assessment'],
                                type=tca['type'],
                                answer=assessment.answer
                            )
                        )
                    else:
                        return_results.append(
                            StudentTeachingContinuousCourseAssessmentNode(
                                uid=None,
                                has_answer=False,
                                assessment_id=tca['id'],
                                assessment=tca['assessment'],
                                type=tca['type'],
                                answer=None
                            )
                        )
                    # print(assessment.course_learn_outcome.learning_outcome)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=return_results,
                            message="Teaching And Continuous Course Assessment Retried Successful")

    @staticmethod
    def register_student_course_learn_outcome_assessment_result(inputs: StudentCourseLearningOutcomeAssessmentInput) ->Response[None]:
        with session_scope() as session:
            course_registration = session.query(StudentCourseRegistration).filter(
                StudentCourseRegistration.uid == inputs.student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).all()
            if len(course_registration) == 0:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None,
                                message="Student Course Registration is not registered")
            course_registration = course_registration[0]
            for result in inputs.answer:
                lean_outcome = session.query(CourseLearnOutcome).filter(
                    CourseLearnOutcome.uid == result.course_lean_outcome_uid).one()
                check_assessment_result = session.query(CourseLearnOutcomeStudentAssessments).filter(
                    CourseLearnOutcomeStudentAssessments.deleted_at.is_(None),
                    CourseLearnOutcomeStudentAssessments.course_learn_outcome_id == lean_outcome.id,
                    CourseLearnOutcomeStudentAssessments.student_course_registration_id == course_registration.id
                ).all()
                if check_assessment_result:
                    assessment_result = check_assessment_result[0]
                    session.query(CourseLearnOutcomeStudentAssessments).filter_by(id=assessment_result.id).update(
                        {"answer": result.answer}
                    )
                else:
                    register = CourseLearnOutcomeStudentAssessments(
                        answer=result.answer,
                        course_learn_outcome_id=lean_outcome.id,
                        student_course_registration_id=course_registration.id
                    )
                    session.add(register)
            session.commit()
            return Response(status=False, code=ResponseCode.SUCCESS,
                            data=None,
                            message="Successful Student Course Leaning Assessment Added")

    @staticmethod
    def register_teaching_and_continuous_course_assessment(inputs: TeachingContinuousCourseAssessmentInput) ->Response[None]:
        with session_scope() as session:
            course_registration = session.query(StudentCourseRegistration).filter(
                StudentCourseRegistration.uid == inputs.student_course_registration_uid,
                StudentCourseRegistration.deleted_at.is_(None)).all()
            if len(course_registration) == 0:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None,
                                message="Student Course Registration is not registered")
            course_registration = course_registration[0]
            for result in inputs.answers:
                # Get student teaching and continuous assessment answer
                check_assessment_result = session.query(TeachingAndContinuousCourseAssessmentResult).filter(
                    TeachingAndContinuousCourseAssessmentResult.deleted_at.is_(None),
                    TeachingAndContinuousCourseAssessmentResult.assessment_id == result.assessment_id,
                    TeachingAndContinuousCourseAssessmentResult.student_course_registration_id == course_registration.id).all()
                if check_assessment_result:
                    assessment_result = check_assessment_result[0]
                    session.query(TeachingAndContinuousCourseAssessmentResult).filter_by(id=assessment_result.id).update(
                        {"answer": result.answer}
                    )
                else:
                    register = TeachingAndContinuousCourseAssessmentResult(
                        answer=result.answer,
                        assessment_id=result.assessment_id,
                        student_course_registration_id=course_registration.id
                    )
                    session.add(register)
            session.commit()
            return Response(status=False, code=ResponseCode.SUCCESS,
                            data=None,
                            message="Successful Teaching And Continuous Course Assessment Added")
