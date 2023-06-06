from typing import List

import strawberry

from src.modules.sr2_api_calls.service import Sr2ApiCalls
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, FeeStructureNode


@strawberry.type
class Sr2Query:
    @strawberry.field
    def get_fee_structure(self, inputs: FeeStructureInput) -> Response[List[FeeStructureNode] | None]:
        try:
            result = Sr2ApiCalls.request_fee_structure(inputs)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=False,
                code=ResponseCode.SUCCESS,
                message="Program not found",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Fee Structure Found",
                data=None)


