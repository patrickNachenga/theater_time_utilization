from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import SeminarType
from src.modules.seminar_types.service import SeminarTypeService, SeminarTypeCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import SeminarTypeInput, SeminarTypeNode, SeminarTypeListNode, PaginationInput


@strawberry.type
class SeminarTypeQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_CATEGORIES"])])
    def get_seminar_types(self, pagination: PaginationInput) -> Response[SeminarTypeListNode]:
        try:
            result = SeminarTypeCrud.get_multi_paginated(pagination, ["description", "name"],
                                                         SeminarTypeListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Seminar Types Retrieved successfully",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_CATEGORIES"])])
    def get_seminar_type(self, uid: str) -> Response[SeminarTypeNode]:
        try:
            result = SeminarTypeService(SeminarType).get_seminar_type_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Seminar Types Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Seminar Type not found",
                data=None)


@strawberry.type
class SeminarTypeMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_COURSE_CATEGORIES"])])
    def register_seminar_type(self, inputs: List[SeminarTypeInput]) -> Response[SeminarTypeListNode]:
        try:
            return SeminarTypeService(SeminarType).register_seminar_type(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Seminar Type not found",
                data=None)

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_COURSE_CATEGORY"])])
    async def remove_seminar_type(self, uid: str) -> Response[None]:
        """
        Remove Seminar Type by UID
        :param uid:
        :return:
        """
        try:
            SeminarTypeService.remove_seminar_type(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Seminar Type Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Seminar Type",
                data=None
            )
