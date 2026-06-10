from typing import List
from src.modules import CRUDBase
from src.models import TheatreRecordDelay
from src.modules.theatre_record_delay.types import TheatreRecordDelayInput, TheatreRecordDelayListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreRecordDelayService(CRUDBase[TheatreRecordDelay, TheatreRecordDelayInput, TheatreRecordDelayInput]):
    def register(self, inputs: List[TheatreRecordDelayInput]) -> Response[TheatreRecordDelayListNode]:
        try:
            result = self.create_or_update('record_uid', inputs, TheatreRecordDelayListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordDelayListNode(items=[], total_count=0))


TheatreRecordDelayCrud = TheatreRecordDelayService(TheatreRecordDelay)
