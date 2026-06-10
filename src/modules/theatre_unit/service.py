from typing import List
from src.modules import CRUDBase
from src.models import TheatreUnit
from src.modules.theatre_unit.types import TheatreUnitInput, TheatreUnitListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreUnitService(CRUDBase[TheatreUnit, TheatreUnitInput, TheatreUnitInput]):
    def register(self, inputs: List[TheatreUnitInput]) -> Response[TheatreUnitListNode]:
        try:
            result = self.create_or_update('name', inputs, TheatreUnitListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreUnitListNode(items=[], total_count=0))


TheatreUnitCrud = TheatreUnitService(TheatreUnit)
