import strawberry
from typing import List

from src.models import ProcedureDelayCause
from src.modules.procedure_delay_cause.service import ProcedureDelayCauseService, ProcedureDelayCauseCrud
from src.modules.procedure_delay_cause.types import ProcedureDelayCauseInput, ProcedureDelayCauseListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class ProcedureDelayCauseQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROCEDURE_DELAY_CAUSES"])])
    def get_procedure_delay_causes(self, pagination: PaginationInput) -> Response[ProcedureDelayCauseListNode]:
        try:
            result = ProcedureDelayCauseCrud.get_multi_paginated(pagination, ['name', 'code', 'description'], ProcedureDelayCauseListNode, [ProcedureDelayCause.procedure_delay_category])
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCauseListNode(items=[], total_count=0))


@strawberry.type
class ProcedureDelayCauseMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROCEDURE_DELAY_CAUSES"])])
    def register_procedure_delay_causes(self, inputs: List[ProcedureDelayCauseInput]) -> Response[ProcedureDelayCauseListNode]:
        try:
            return ProcedureDelayCauseService(ProcedureDelayCauseCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCauseListNode(items=[], total_count=0))
