from typing import List, Optional

import requests
import strawberry

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import LoginRequiredExtension, Info, Context
from src.modules.program_course.service import ProgramCourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import MoodleGetUrlInput, MoodleGetQuizzesInput, \
    MoodleGradingMethodNode, MoodleUsersAttemptsOnQuizInput, \
    MoodleUsersAttemptsOnQuizNode


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
    def get_moodle_quizzes_by_course(self, inputs: MoodleGetQuizzesInput) -> Response[str]:
        try:
            moodle = MoodleApi()
            moodle_response = moodle.get_quizzes_by_course(course_id=inputs.course_moodle_id)
            if moodle_response:
                print(moodle_response)
                return Response(status=False, code=ResponseCode.SUCCESS,
                                message="Moodle Quizzes Retrieved Successful",
                                data=moodle_response)
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
                return Response(status=False, code=ResponseCode.SUCCESS,
                                message="Moodle Quizzes Retrieved Successful",
                                data=moodle_response)
            else:
                return Response(
                    status=False, code=ResponseCode.NO_RECORD_FOUND,
                    message="No moodle grading method found",
                    data=[])
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
            program_course = ProgramCourseService.get_program_course_by_uid(inputs.program_course_uid)
            if program_course:
                students_uids = [course_registrations.student_uid for course_registrations in
                                 program_course.student_course_registrations]
                if students_uids:
                    # go to uaa to get student information
                    params = {"uids": students_uids}
                    response = requests.get(settings.UAA_URi + f'/students-details-by-uids', params=params)
                    response.raise_for_status()
                    if response.status_code == 200:
                        studentData = response.json()
                        # go to moodle for getting user attempt on quiz
                        moodle = MoodleApi()
                        user_moodle_ids = [student.moodle_id for student in studentData if
                                           student.user.moodle_id is not None]
                        moodle_response = moodle.get_user_attempts_on_quiz(quiz_id=inputs.quiz_id,
                                                                           grading_method=inputs.grading_method,
                                                                           user_id=user_moodle_ids)
                        if moodle_response:
                            moodleQuizResult = []
                            for quizData in moodle_response:
                                student = next((student for student in studentData if
                                                student.user.moodle_id == quizData['userid']), None)
                                if student:
                                    moodleQuizResult.append(
                                        MoodleUsersAttemptsOnQuizNode(
                                            registration_number=student.registration_number,
                                            full_name=student.full_name,
                                            moodle_id=student.moodle_id,
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
