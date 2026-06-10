import strawberry
from typing import List

from src.modules.external_source.service import ExternalSourceService, ExternalSourceCrud
from src.modules.external_source.types import ExternalSourceInput, ExternalSourceListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class ExternalSourceQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_EXTERNAL_SOURCES"])])
    def get_external_sources(self, pagination: PaginationInput) -> Response[ExternalSourceListNode]:
        try:
            result = ExternalSourceCrud.get_multi_paginated(pagination, ['name', 'code'], ExternalSourceListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ExternalSourceListNode(items=[], total_count=0))


@strawberry.type
class ExternalSourceMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_EXTERNAL_SOURCES"])])
    def register_external_sources(self, inputs: List[ExternalSourceInput]) -> Response[ExternalSourceListNode]:
        try:
            return ExternalSourceService(ExternalSourceCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ExternalSourceListNode(items=[], total_count=0))
