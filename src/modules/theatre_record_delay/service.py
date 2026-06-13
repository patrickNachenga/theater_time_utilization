from typing import List
from src.modules import CRUDBase
from src.models import TheatreRecordDelay
from src.modules.theatre_record_delay.types import TheatreRecordDelayInput, TheatreRecordDelayListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.theatre_procedure_record.service import TheatreTimeRecordCrud
from src.modules.procedure_delay_category.service import ProcedureDelayCategoryCrud
from src.modules.procedure_delay_cause.service import ProcedureDelayCauseCrud


class TheatreRecordDelayService(CRUDBase[TheatreRecordDelay, TheatreRecordDelayInput, TheatreRecordDelayInput]):
    def register(self, inputs: List[TheatreRecordDelayInput]) -> Response[TheatreRecordDelayListNode]:
        try:
            processed_inputs = []
            for input_obj in inputs:
                new_input_obj = input_obj.copy() # Create a copy to avoid modifying the original input

                if new_input_obj.record_uid:
                    record = TheatreTimeRecordCrud.get(new_input_obj.record_uid)
                    if not record:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Theatre Record with UID {new_input_obj.record_uid} not found.",
                                        data=TheatreRecordDelayListNode(items=[], total_count=0))
                    new_input_obj.record_id = record.id
                    new_input_obj.record_uid = None

                if new_input_obj.procedure_delay_category_uid:
                    category = ProcedureDelayCategoryCrud.get(new_input_obj.procedure_delay_category_uid)
                    if not category:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Procedure Delay Category with UID {new_input_obj.procedure_delay_category_uid} not found.",
                                        data=TheatreRecordDelayListNode(items=[], total_count=0))
                    new_input_obj.procedure_delay_category_id = category.id
                    new_input_obj.procedure_delay_category_uid = None

                if new_input_obj.delay_cause_uid:
                    cause = ProcedureDelayCauseCrud.get(new_input_obj.delay_cause_uid)
                    if not cause:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Procedure Delay Cause with UID {new_input_obj.delay_cause_uid} not found.",
                                        data=TheatreRecordDelayListNode(items=[], total_count=0))
                    new_input_obj.delay_cause_id = cause.id
                    new_input_obj.delay_cause_uid = None

                processed_inputs.append(new_input_obj)

            result = self.create_or_update('record_id', processed_inputs, TheatreRecordDelayListNode) # Assuming record_id is a suitable unique field for update checks
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordDelayListNode(items=[], total_count=0))


TheatreRecordDelayCrud = TheatreRecordDelayService(TheatreRecordDelay)