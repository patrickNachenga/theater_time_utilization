from typing import List

import strawberry

from src.models import ByLaw
from src.modules.by_law.service import ByLawCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput, ByLawListNode, \
    ByLawNode, ByLawInput


@strawberry.type
class ByLawQuery:
    # extensions=[CustomPermissionExtension(["VIEW_ACADEMIC_YEARS"])]
    @strawberry.field()
    def get_by_laws(self, pagination: PaginationInput) -> Response[ByLawListNode]:
        try:
            result = ByLawCrud.get_multi_paginated(pagination, ['name', 'code', 'status', 'start_date', 'end_date'],
                                                   ByLawListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="By law retrieved successfully",
            data=result,
        )

    @strawberry.field()
    def get_by_law_by_uid(self, uid: str) -> Response[ByLawNode]:
        try:
            result = ByLawCrud.get_by_law_by_uid(uid)
        except Exception as e:
            print(e)
            result = []

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="By-law retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="By-law not found",
                data=None)

    @strawberry.field()
    def get_active_by_law(self) -> Response[ByLawNode]:
        try:
            result = ByLawCrud.get_active_by_law()
        except Exception as e:
            print(e)
            result = None

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Active By-law retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Active By-law found",
                data=None)


@strawberry.type
class ByLawMutation:
    @strawberry.field()
    def register_by_law(self, inputs: ByLawInput) -> Response[ByLawListNode]:
        try:
            return ByLawCrud.register_by_law(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Add By-law",
                            data=ByLawListNode(items=[], total_count=0))

    @strawberry.mutation()
    async def remove_by_law(self, uid: str) -> Response[ByLawListNode]:
        """
        Remove Academic Year By UID
        :param uid:
        :return:
        """
        try:
            return ByLawCrud.remove_by_law(uid)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Remove By-law",
                            data=ByLawListNode(items=[], total_count=0))
