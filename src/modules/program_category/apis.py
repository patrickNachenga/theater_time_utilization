from typing import List

import strawberry

from src.modules.program_category.service import ProgramCategoryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCategoryInput, ProgramCategoryNode


@strawberry.type
class ProgramCategoryQuery:
    @strawberry.field
    def get_program_category(self) -> Response[List[ProgramCategoryNode]]:
        try:
            result = ProgramCategoryService.get_program_categories()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Program Category",
            data=result)


@strawberry.type
class ProgramCategoryMutation:
    @strawberry.field
    def register_program_category(self, inputs: List[ProgramCategoryInput]) -> Response[List[ProgramCategoryNode]]:
        try:
            return ProgramCategoryService().register_program_categories(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Register Program Category",
                            data=[])

    #Delete program type function
    @strawberry.mutation
    async def remove_program_category(self, uid: str) -> Response[None]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            ProgramCategoryService().remove_program_category(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Category Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Program Category",
                data=None
            )