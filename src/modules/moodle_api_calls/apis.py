from typing import List, Optional

import requests
import strawberry

from src.core.moodle_api import MoodleApi
from src.core.security import LoginRequiredExtension, Info, Context
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import MoodleGetUrlInput


@strawberry.type
class MoodleApiCallQuery:
    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_moodle_url(self, inputs: MoodleGetUrlInput, info: Info) -> Response[Optional[str]]:
        try:
            if info and info.context.user.profile.moodle_username:
                moodle_username = info.context.user.profile.moodle_username
                moodle = MoodleApi()
                moodle_response = moodle.getloginurl(moodle_username,  course_id=inputs.course_moodle_id)
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
                    message="Failed to get moodle access",
                    data=None)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Unable To Get Moodle Verification",
                data=None)


@strawberry.type
class MoodleApiCallMutation:
    pass
