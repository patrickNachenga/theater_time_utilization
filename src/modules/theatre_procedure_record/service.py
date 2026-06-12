from typing import List
from src.modules import CRUDBase
from src.models import TheatreProcedureRecord
from src.modules.theatre_procedure_record.types import TheatreTimeRecordInput, TheatreTimeRecordListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreTimeRecordService(CRUDBase[TheatreProcedureRecord, TheatreTimeRecordInput, TheatreTimeRecordInput]):
    def register(self, inputs: List[TheatreTimeRecordInput]) -> Response[TheatreTimeRecordListNode]:
        try:
            result = self.create_or_update('patient_mrn', inputs, TheatreTimeRecordListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreTimeRecordListNode(items=[], total_count=0))


TheatreTimeRecordCrud = TheatreTimeRecordService(TheatreProcedureRecord)
