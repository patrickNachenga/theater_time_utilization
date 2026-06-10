from typing import List
from src.modules import CRUDBase
from src.models import TheatreTimeRecord
from src.modules.theatre_time_record.types import TheatreTimeRecordInput, TheatreTimeRecordListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreTimeRecordService(CRUDBase[TheatreTimeRecord, TheatreTimeRecordInput, TheatreTimeRecordInput]):
    def register(self, inputs: List[TheatreTimeRecordInput]) -> Response[TheatreTimeRecordListNode]:
        try:
            result = self.create_or_update('patient_mrn', inputs, TheatreTimeRecordListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreTimeRecordListNode(items=[], total_count=0))


TheatreTimeRecordCrud = TheatreTimeRecordService(TheatreTimeRecord)
