from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import SeminarTypes
from src.modules.seminar_types.service import SeminarTypesService, SeminarTypesCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import SeminarTypesInput, SeminarTypesNode, SeminarTypesListNode, PaginationInput


@strawberry.type
class SeminarTypeQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_CATEGORIES"])])
    def get_seminar_types(self, pagination: PaginationInput) -> Response[SeminarTypesListNode]:
        try:
            result = SeminarTypesListNode.get_multi_paginated(pagination, ["description", "name"],
                                                            SeminarTypesListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Seminar Types Retrieved successfully",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_CATEGORIES"])])
    def get_seminar_type(self, uid: str) -> Response[SeminarTypesNode]:
        try:
            result = SeminarTypesService(SeminarTypes).get_seminar_type_by_uid(uid)
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
    def register_course_categories(self, inputs: List[SeminarTypesInput]) -> Response[SeminarTypesListNode]:
        try:
            return SeminarTypesService(SeminarTypes).register_seminar_types(inputs)
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
            SeminarTypesService.remove_seminar_type(uid)
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
