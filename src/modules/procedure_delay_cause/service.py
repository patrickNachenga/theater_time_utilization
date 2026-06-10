from typing import List
from src.modules import CRUDBase
from src.models import ProcedureDelayCause
from src.modules.procedure_delay_cause.types import ProcedureDelayCauseInput, ProcedureDelayCauseListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class ProcedureDelayCauseService(CRUDBase[ProcedureDelayCause, ProcedureDelayCauseInput, ProcedureDelayCauseInput]):
    def register(self, inputs: List[ProcedureDelayCauseInput]) -> Response[ProcedureDelayCauseListNode]:
        try:
            result = self.create_or_update('name', inputs, ProcedureDelayCauseListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCauseListNode(items=[], total_count=0))


ProcedureDelayCauseCrud = ProcedureDelayCauseService(ProcedureDelayCause)
