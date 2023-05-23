from typing import List

import strawberry

from src.modules.exam_cats.service import ExamCatsService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCatsNode, ExamCatsInput


@strawberry.type
class ExamCatsQuery:
    @strawberry.field
    def get_exam_cats(self) -> Response[List[ExamCatsNode]]:
        try:
            result = ExamCatsService.get_exam_cats()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Exam Category retrieved successfully",
            data=result)


@strawberry.type
class ExamCatsMutation:
    @strawberry.field
    def register_exam_cats(self, inputs: List[ExamCatsInput]) -> Response[List[ExamCatsNode]]:
        try:
            return ExamCatsService().register_get_exam_cats(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to register Examination Category", data=[])

    # delete programme
    @strawberry.mutation
    async def remove_exam_cats(self, uid: str) -> Response[None]:
        """
        Remove Exam Category By UID
        :param uid:
        :return:
        """
        try:
            ExamCatsService.remove_exam_cats(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Category Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Exam Category",
                data=None
            )
