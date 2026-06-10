import strawberry
from typing import List

from src.modules.region.service import RegionService, RegionCrud
from src.modules.region.types import RegionInput, RegionListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class RegionQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_REGIONS"])])
    def get_regions(self, pagination: PaginationInput) -> Response[RegionListNode]:
        try:
            result = RegionCrud.get_multi_paginated(pagination, ['name', 'code'], RegionListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=RegionListNode(items=[], total_count=0))


@strawberry.type
class RegionMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_REGIONS"])])
    def register_regions(self, inputs: List[RegionInput]) -> Response[RegionListNode]:
        try:
            return RegionService(RegionCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=RegionListNode(items=[], total_count=0))
