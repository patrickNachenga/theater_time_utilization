from typing import List
from src.modules import CRUDBase
from src.models import ProcedureDelayCause
from src.modules.procedure_delay_cause.types import ProcedureDelayCauseInput, ProcedureDelayCauseListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.procedure_delay_category.service import ProcedureDelayCategoryCrud


class ProcedureDelayCauseService(CRUDBase[ProcedureDelayCause, ProcedureDelayCauseInput, ProcedureDelayCauseInput]):
    def register(self, inputs: List[ProcedureDelayCauseInput]) -> Response[ProcedureDelayCauseListNode]:
        try:
            processed_inputs = []
            for input_obj in inputs:
                new_input_obj = input_obj.copy() # Create a copy to avoid modifying the original input
                if new_input_obj.procedure_delay_category_uid:
                    category = ProcedureDelayCategoryCrud.get(new_input_obj.procedure_delay_category_uid)
                    if not category:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Procedure Delay Category with UID {new_input_obj.procedure_delay_category_uid} not found.",
                                        data=ProcedureDelayCauseListNode(items=[], total_count=0))
                    new_input_obj.procedure_delay_category_id = category.id
                    new_input_obj.procedure_delay_category_uid = None  # Clear UID to avoid conflicts
                processed_inputs.append(new_input_obj)

            result = self.create_or_update('name', processed_inputs, ProcedureDelayCauseListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCauseListNode(items=[], total_count=0))


ProcedureDelayCauseCrud = ProcedureDelayCauseService(ProcedureDelayCause)