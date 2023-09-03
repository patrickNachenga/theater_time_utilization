import json
from typing import List

import requests
import strawberry
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import LoginRequiredExtension, Info
from src.db.session import session_scope
from src.models import ProgramCourse, StudentCourseRegistration
from src.modules.program_course.service import ProgramCourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import MoodleGetUrlInput, MoodleGetQuizzesInput, \
    MoodleGradingMethodNode, MoodleUsersAttemptsOnQuizInput, \
    MoodleUsersAttemptsOnQuizNode, MoodleQuizNode, MoodleCourseQuizzesNode, ProgramCourseNode


@strawberry.type
class MoodleApiCallQuery:
    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_moodle_url(self, inputs: MoodleGetUrlInput, info: Info) -> Response[str]:
        try:
            if info and info.context.user.profile.moodle_username:
                moodle_username = info.context.user.profile.moodle_username
                moodle = MoodleApi()
                moodle_response = moodle.getloginurl(moodle_username, course_id=inputs.course_moodle_id)
                if moodle_response:
                    return Response(status=False, code=ResponseCode.SUCCESS,
                                    message="Moodle Url Retrieved Successful",
                                    data=moodle_response)
                else:
                    return Response(
                        status=False, code=ResponseCode.RESTRICTED_ACCESS,
                        message="Failed to get moodle access",
                        data=None)
            else:
                return Response(
                    status=False, code=ResponseCode.RESTRICTED_ACCESS,
                    message="Unable to access moodle",
                    data=None)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Unable To Get Moodle Verification",
                data=None)

    @strawberry.field(extensions=[LoginRequiredExtension()])
    async def get_moodle_quizzes_by_course(self, inputs: MoodleGetQuizzesInput) -> Response[MoodleCourseQuizzesNode]:
        try:
            moodle = MoodleApi()
            moodle_response = moodle.get_quizzes_by_course(course_id=inputs.course_moodle_id)
            if moodle_response:
                quizzes = [MoodleQuizNode(**quiz_data) for quiz_data in moodle_response]
                return Response(status=False, code=ResponseCode.SUCCESS,
                                message="Moodle Quizzes Retrieved Successful",
                                data=MoodleCourseQuizzesNode(
                                    quizzes=quizzes
                                )
                                )
            else:
                return Response(
                    status=False, code=ResponseCode.NO_RECORD_FOUND,
                    message="No moodle Quizzes Found",
                    data=None)

        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Unable To Get Moodle Quizzes",
                data=None)

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_moodle_grading_method(self) -> Response[List[MoodleGradingMethodNode]]:
        try:
            moodle = MoodleApi()
            moodle_response = moodle.grading_method()
            if moodle_response:
                moodle_grading_methods = [MoodleGradingMethodNode(id=grading_method['id'], name=grading_method['name'])
                                          for grading_method in moodle_response]
                return Response(status=False, code=ResponseCode.SUCCESS,
                                message="Moodle Quizzes Methode Retrieved Successful",
                                data=moodle_grading_methods)
            else:
                return Response(
                    status=False, code=ResponseCode.NO_RECORD_FOUND,
                    message="No moodle grading method found",
                    data=[]
                )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Unable To Get Moodle grading method",
                data=[])

    # @strawberry.field(extensions=[LoginRequiredExtension()])
    # def get_moodle_user_attempts_on_quiz(self, inputs: MoodleUserAttemptsOnQuizInput) -> Response[List[str]]:
    #     try:
    #         moodle = MoodleApi()
    #         moodle_response = moodle.get_user_attempts_on_quiz(quiz_id=inputs.quiz_id,
    #                                                            grading_method=inputs.grading_method,
    #                                                            user_id=inputs.user_moodle_id)
    #         print(moodle_response)
    #         if moodle_response:
    #             return Response(status=False, code=ResponseCode.SUCCESS,
    #                             message="Moodle User Attempts on Quizzes Retrieved Successful",
    #                             data=moodle_response)
    #         else:
    #             return Response(
    #                 status=False, code=ResponseCode.NO_RECORD_FOUND,
    #                 message="No records for Moodle User Attempts on Quizzes",
    #                 data=[])
    #     except Exception as e:
    #         print(e)
    #         return Response(
    #             status=False,
    #             code=ResponseCode.FAILURE,
    #             message="Unable To Get Moodle User Attempts on Quizzes ",
    #             data=[])

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_moodle_users_attempts_on_quiz(self, inputs: MoodleUsersAttemptsOnQuizInput) -> Response[List[MoodleUsersAttemptsOnQuizNode]]:
        try:
            with session_scope() as session:
                student_course_registrations = session.query(StudentCourseRegistration).join(ProgramCourse, ProgramCourse.id == StudentCourseRegistration.program_course_id) \
                    .filter(StudentCourseRegistration.deleted_at.is_(None))\
                    .filter(ProgramCourse.uid == inputs.program_course_uid).all()

                if student_course_registrations:
                    students_uids = [course_registration.student_uid for course_registration in student_course_registrations]
                    if students_uids:
                        # go to uaa to get student information
                        data_obj = {
                            "uids": students_uids
                        }

                        # Serialize the data to JSON
                        json_data = json.dumps(data_obj)

                        # Set the Content-Type header to indicate that the request body is JSON
                        headers = {
                            "Content-Type": "application/json"
                        }
                        # Send the Get request
                        response = requests.post(settings.UAA_URi + f'/students-details-by-uids', data=json_data, headers=headers)
                        response.raise_for_status()
                        if response.status_code == 200:
                            responseData = response.json()
                            studentData = responseData['data']
                            if studentData:
                                # go to moodle for getting user attempt on quiz
                                moodle = MoodleApi()
                                user_moodle_ids = [student['user']['moodle_id'] for student in studentData if
                                                   'user' in student and 'moodle_id' in student['user'] and student['user'][
                                                       'moodle_id'] is not None]
                                moodle_response = moodle.get_users_attempts_on_quiz(quiz_id=inputs.quiz_id, grading_method=inputs.grading_method, user_id_array=user_moodle_ids)
                                if moodle_response:
                                    moodleQuizResult = []
                                    for quizData in moodle_response:
                                        student = next((student for student in studentData if student['user']['moodle_id'] == quizData['userid']), None)
                                        if student:
                                            moodleQuizResult.append(
                                                MoodleUsersAttemptsOnQuizNode(
                                                    registration_number=student['registration_number'],
                                                    full_name=student['full_name'],
                                                    moodle_id=student['user']['moodle_id'],
                                                    grade=quizData['grades']
                                                )
                                            )
                                    return Response(status=False, code=ResponseCode.SUCCESS,
                                                    message="Moodle User Attempts on Quizzes Retrieved Successful",
                                                    data=moodleQuizResult)
                                else:
                                    return Response(
                                        status=False, code=ResponseCode.NO_RECORD_FOUND,
                                        message="No records for Moodle User Attempts on Quizzes",
                                        data=[])
                            else:
                                return Response(
                                    status=False, code=ResponseCode.NO_RECORD_FOUND,
                                    message="No Student records found for Moodle Attempts on Quizzes",
                                    data=[])
                        else:
                            return Response(
                                status=False, code=ResponseCode.NO_RECORD_FOUND,
                                message="Student records not found",
                                data=[])
                    else:
                        return Response(
                            status=False, code=ResponseCode.NO_RECORD_FOUND,
                            message="No Student Found under this course",
                            data=[])
                else:
                    return Response(
                        status=False, code=ResponseCode.NO_RECORD_FOUND,
                        message="Unable to get program course data",
                        data=[]
                    )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Unable To Get Moodle User Attempts on Quizzes ",
                data=[])


@strawberry.type
class MoodleApiCallMutation:
    pass
