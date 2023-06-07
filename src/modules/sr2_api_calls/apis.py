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

<<<<<<< HEAD

=======
    @strawberry.field
    def get_control_number(self, inputs: FeeStructureInput) -> Response[List[FeeStructureNode] | None]:
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
>>>>>>> f6c1bcacea4d7921ee708b1416f5cbbc1e42806d
