from typing import List, Any

import strawberry

from src.modules.sr2_api_calls.service import Sr2ApiCalls
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, FeeStructureNode, ControlNumberInput


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
                status=True,
                code=ResponseCode.SUCCESS,
                message=f"Fee Structure for {inputs.program_code} retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Fee Structure Found",
                data=None)

    @strawberry.field
    def get_control_number(self, inputs: ControlNumberInput) -> Response[None]:
        try:
            result = Sr2ApiCalls.generate_control_number(inputs)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Invoice Generate",
                data=None)
        else:
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Fail To Generate",
                data=None)
