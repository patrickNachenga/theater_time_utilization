from typing import List

import strawberry

from src.modules.sr2_api_calls.service import Sr2ApiCalls
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, FeeStructureNode, ControlNumberInput


@strawberry.type
class FeeStructureMutation:
    @strawberry.field
    def request_fee_structure(self, inputs: FeeStructureInput) -> Response[List[FeeStructureNode] | None]:
        try:
            return Sr2ApiCalls.request_fee_structure(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve fee structure",
                data=None)

    @strawberry.field
    def get_control_number(self, inputs: ControlNumberInput) -> Response[None]:
        try:
            return Sr2ApiCalls.request_control_numbers(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to generate control number",
                data=None)
