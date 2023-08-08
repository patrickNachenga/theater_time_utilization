from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.exam_category_groups.service import ExamCategoryGroupsService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCategoryGroupsInput, ExamCategoryGroupsNode


@strawberry.type
class ExamCategoryGroupsQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_EXAM_CATEGORY_GROUPS"])])
    def get_exam_category_groups(self) -> Response[Optional[List[ExamCategoryGroupsNode]]]:
        try:
            result = ExamCategoryGroupsService.get_exam_category_groups()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Exam Category Group Category",
            data=result)


@strawberry.type
class ExamCategoryGroupsMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_EXAM_CATEGORY_GROUPS"])])
    def register_exam_category_groups(self, inputs: List[ExamCategoryGroupsInput]) -> Response[
        Optional[List[ExamCategoryGroupsNode]]]:
        try:
            return ExamCategoryGroupsService().register_exam_category_groups(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Category", data=[])

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_EXAM_CATEGORY_GROUP"])])
    async def remove_exam_category_group(self, uid: str) -> Response[None]:
        """
        Remove exam category group By UID
        :param uid:
        :return:
        """
        try:
            ExamCategoryGroupsService.remove_exam_category_group(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Category Group Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Exam Category Group",
                data=None
            )
