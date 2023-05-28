from typing import List

import strawberry

from src.models import ProgramCategory
from src.modules.program_category.service import ProgramCategoryService, ProgramCategoryCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCategoryInput, ProgramCategoryNode, ProgramCategoryListNode, PaginationInput


@strawberry.type
class ProgramCategoryQuery:
    @strawberry.field
    def get_program_category(self, pagination: PaginationInput) -> Response[ProgramCategoryListNode]:
        try:
            result = ProgramCategoryCrud.get_multi_paginated(pagination, ['name', 'short_name'],
                                                             ProgramCategoryListNode)
        except Exception as e:
            print(e)
            result = ProgramCategoryListNode(items=[], total_count=0)
        return Response(
            status=False,
            code=ResponseCode.FAILURE,
            message="Successfully Retrieve Program Category",
            data=result)


@strawberry.type
class ProgramCategoryMutation:
    @strawberry.field
    def register_program_category(self, inputs: List[ProgramCategoryInput]) -> Response[ProgramCategoryListNode]:
        try:
            return ProgramCategoryService(ProgramCategory).register_program_categories(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Register Program Category",
                            data=[])

    # Delete programs type function
    @strawberry.mutation
    async def remove_program_category(self, uid: str) -> Response[None]:
        """
        Remove Program Category By UID
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
