import strawberry
from typing import List

from src.modules.procedure_delay_category.service import ProcedureDelayCategoryService, ProcedureDelayCategoryCrud
from src.modules.procedure_delay_category.types import ProcedureDelayCategoryInput, ProcedureDelayCategoryListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class ProcedureDelayCategoryQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROCEDURE_DELAY_CATEGORIES"])])
    def get_procedure_delay_categories(self, pagination: PaginationInput) -> Response[ProcedureDelayCategoryListNode]:
        try:
            result = ProcedureDelayCategoryCrud.get_multi_paginated(pagination, ['name', 'code', 'description'], ProcedureDelayCategoryListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCategoryListNode(items=[], total_count=0))


@strawberry.type
class ProcedureDelayCategoryMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROCEDURE_DELAY_CATEGORIES"])])
    def register_procedure_delay_categories(self, inputs: List[ProcedureDelayCategoryInput]) -> Response[ProcedureDelayCategoryListNode]:
        try:
            return ProcedureDelayCategoryService(ProcedureDelayCategoryCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCategoryListNode(items=[], total_count=0))
