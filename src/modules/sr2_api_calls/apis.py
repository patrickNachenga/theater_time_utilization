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

# @strawberry.type
# class Sr2Mutation:
#     @strawberry.field
#     def request_program_fee_structure(self, inputs: List[AcademicYearInput]) -> Response[AcademicYearListNode]:
#         try:
#             return AcademicYearService(AcademicYear).register_academic_year(inputs)
#         except Exception as e:
#             print(e)
#             return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Add Academic Year", data=AcademicYearListNode(items=[], total_count=0))
#
#     @strawberry.mutation
#     async def remove_academic_year(self, uid: str) -> Response[None]:
#         """
#         Remove Academic Year By UID
#         :param uid:
#         :return:
#         """
#         try:
#             AcademicYearService(AcademicYear).remove_academic_year(uid)
#             return Response(
#                 status=True,
#                 code=ResponseCode.SUCCESS,
#                 message="Academic Year Removed Successfully",
#                 data=None
#             )
#         except Exception as e:
#             print(e)
#             return Response(
#                 status=False,
#                 code=ResponseCode.FAILURE,
#                 message="Failed to Remove Academic Year",
#                 data=None
#             )
