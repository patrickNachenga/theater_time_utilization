# from typing import List, Any
#
# import strawberry
#
# from src.shared.response import Response
# from src.shared.response_code import ResponseCode
# from src.types import PaginationInput, ProgramFeeStructureInput
#
#
# @strawberry.type
# class AcademicYearQuery:
#     @strawberry.field
#     def get_fee_structure(self, inputs: ProgramFeeStructureInput) -> Response[Any]:
#         try:
#
#             return Response(
#                 status=True,
#                 # code=ResponseCode.SUCCESS,
#                 message="Academic Year retrieved successfully",
#                 data=[])
#         except Exception as e:
#             print(e)
#             return Response(
#                 status=False,
#                 code=ResponseCode.FAILURE,
#                 message="Unable to get Fee Structure",
#                 data=None)
#
# # @strawberry.type
# # class AcademicYearMutation:
#     # @strawberry.field
#     # def request_program_fee_structure(self, inputs: List[AcademicYearInput]) -> Response[AcademicYearListNode]:
#     #     try:
#     #         return AcademicYearService(AcademicYear).register_academic_year(inputs)
#     #     except Exception as e:
#     #         print(e)
#     #         return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Add Academic Year", data=AcademicYearListNode(items=[], total_count=0))
#     #
#     # @strawberry.mutation
#     # async def remove_academic_year(self, uid: str) -> Response[None]:
#     #     """
#     #     Remove Academic Year By UID
#     #     :param uid:
#     #     :return:
#     #     """
#     #     try:
#     #         AcademicYearService(AcademicYear).remove_academic_year(uid)
#     #         return Response(
#     #             status=True,
#     #             code=ResponseCode.SUCCESS,
#     #             message="Academic Year Removed Successfully",
#     #             data=None
#     #         )
#     #     except Exception as e:
#     #         print(e)
#     #         return Response(
#     #             status=False,
#     #             code=ResponseCode.FAILURE,
#     #             message="Failed to Remove Academic Year",
#     #             data=None
#     #         )
