from typing import List, Any, Optional

import strawberry

from src.core.security import LoginRequiredExtension
from src.modules.sr2_api_calls.service import Sr2ApiCalls
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, FeeStructureNode, RequestControlNumberInput, ControlNumberNode, \
    RewControlNumberInput


@strawberry.type
class Sr2ApiCallQuery:
    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_fee_structure(self, inputs: FeeStructureInput) -> Response[List[FeeStructureNode] | None]:
        try:
            return Sr2ApiCalls.get_fee_structures(inputs)
        except Exception as e:
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve fee structure",
                data=None)

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_control_numbers(self, registration_number: str) -> Response[List[ControlNumberNode] | None]:
        try:
            result = Sr2ApiCalls.get_student_control_number(registration_number)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Control Numbers Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Control Number not found",
                data=None)

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def get_financial_statement(self, registration_number: str) -> Response[str | None]:
        try:
            return Sr2ApiCalls.get_financial_statement(registration_number)
        except Exception as e:
            return Response(
                status=True,
                code=ResponseCode.FAILURE,
                message="Failed to retrieve financial Statement",
                data=None,
            )


@strawberry.type
class Sr2ApiCallMutation:

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def request_fee_structure_control_numbers(self, inputs: RequestControlNumberInput) -> Response[Optional[str]]:
        try:
            return Sr2ApiCalls.request_control_numbers(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to generate control number request",
                data=None,
            )

    @strawberry.field(extensions=[LoginRequiredExtension()])
    def renew_control_number(self, inputs: RewControlNumberInput) -> Response[Optional[str]]:
        try:
            return Sr2ApiCalls.renew_control_number(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Renew control number request",
                data=None
            )
