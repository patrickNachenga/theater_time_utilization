from typing import List
from src.modules import CRUDBase
from src.models import Region
from src.modules.region.types import RegionInput, RegionListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class RegionService(CRUDBase[Region, RegionInput, RegionInput]):
    def register(self, inputs: List[RegionInput]) -> Response[RegionListNode]:
        try:
            result = self.create_or_update('name', inputs, RegionListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=RegionListNode(items=[], total_count=0))


RegionCrud = RegionService(Region)
