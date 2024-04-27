from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.models import Group
from src.modules.upload_result_deadline.service import UploadResultDeadlineService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import UploadResultDeadlineNode, ResultDeadlineInput


@strawberry.type
class UploadResultDeadlineQuery:
    @strawberry.field()
    # @strawberry.field(extensions=[CustomPermissionExtension(["GET_UPLOAD_RESULT_DEADLINE"])])
    def get_upload_result_deadline(self, info: Info) -> Response[List[UploadResultDeadlineNode]]:
        try:
            result = UploadResultDeadlineService.get_upload_result_deadline(info)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Result Deadline retrieved successfully",
            data=result)


@strawberry.type
class UploadResultDeadlineMutation:
    @strawberry.field()
    def register_upload_result_deadline(self, inputs: ResultDeadlineInput, info: Info) -> Response[None]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=[])
            return UploadResultDeadlineService().register_upload_result_deadline(inputs, info)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Groups", data=[])

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_COURSE"])])
    async def remove_upload_result_deadline(self, uid: str) -> Response[None]:
        """
        Remove Course By UID
        :param uid:
        :return:
        """
        try:
            UploadResultDeadlineService.remove_upload_result_deadline(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Upload Result Deadline Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Upload Result Deadline to Remove Course",
                data=None
            )
