from typing import List

import strawberry

from src.modules.program_type.service import ProgramCategoryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCategoryInput, ProgramCategoryNode


@strawberry.type
class ProgramCategoryQuery:
    @strawberry.field
    def get_program_category(self) -> Response[List[ProgramCategoryNode]]:
        try:
            result = ProgramCategoryService.get_program_category()
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
