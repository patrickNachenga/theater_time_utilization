import strawberry
from typing import List

from src.modules.internal_source.service import InternalSourceService, InternalSourceCrud
from src.modules.internal_source.types import InternalSourceInput, InternalSourceListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class InternalSourceQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_INTERNAL_SOURCES"])])
    def get_internal_sources(self, pagination: PaginationInput) -> Response[InternalSourceListNode]:
        try:
            result = InternalSourceCrud.get_multi_paginated(pagination, ['name', 'code'], InternalSourceListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=InternalSourceListNode(items=[], total_count=0))


@strawberry.type
class InternalSourceMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_INTERNAL_SOURCES"])])
    def register_internal_sources(self, inputs: List[InternalSourceInput]) -> Response[InternalSourceListNode]:
        try:
            return InternalSourceService(InternalSourceCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=InternalSourceListNode(items=[], total_count=0))
