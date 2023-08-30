from typing import List, Optional, Any

import requests
import strawberry

from src.core.moodle_api import MoodleApi
from src.core.security import LoginRequiredExtension, Info, Context
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import MoodleGetUrlInput, MoodleGetQuizzesInput, \
    MoodleGradingMethodNode, MoodleUserAttemptsOnQuizInput, MoodleUsersAttemptsOnQuizInput


@strawberry.type
class MoodleApiCallQuery:
    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_moodle_url(self, inputs: MoodleGetUrlInput, info: Info) -> Response[Optional[str]]:
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
    def get_moodle_quizzes_by_course(self, inputs: MoodleGetQuizzesInput) -> Response[Optional[str]]:
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

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_moodle_user_attempts_on_quiz(self, inputs: MoodleUserAttemptsOnQuizInput) -> Response[List[str]]:
        try:
            moodle = MoodleApi()
            moodle_response = moodle.get_user_attempts_on_quiz(quiz_id=inputs.quiz_id,
                                                               grading_method=inputs.grading_method,
                                                               user_id=inputs.user_moodle_id)
            print(moodle_response)
            if moodle_response:
                return Response(status=False, code=ResponseCode.SUCCESS,
                                message="Moodle User Attempts on Quizzes Retrieved Successful",
                                data=moodle_response)
            else:
                return Response(
                    status=False, code=ResponseCode.NO_RECORD_FOUND,
                    message="No records for Moodle User Attempts on Quizzes",
                    data=[])
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Unable To Get Moodle User Attempts on Quizzes ",
                data=[])

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_moodle_users_attempts_on_quiz(self, inputs: MoodleUsersAttemptsOnQuizInput) -> Response[Optional[str]]:
        try:
            moodle = MoodleApi()
            moodle_response = moodle.get_user_attempts_on_quiz(quiz_id=inputs.quiz_id,
                                                               grading_method=inputs.grading_method,
                                                               user_id=inputs.user_moodle_id)
            if moodle_response:
                return Response(status=False, code=ResponseCode.SUCCESS,
                                message="Moodle User Attempts on Quizzes Retrieved Successful",
                                data=moodle_response)
            else:
                return Response(
                    status=False, code=ResponseCode.NO_RECORD_FOUND,
                    message="No records for Moodle User Attempts on Quizzes",
                    data=[])
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
