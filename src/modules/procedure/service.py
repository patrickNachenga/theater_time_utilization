from typing import List
from src.modules import CRUDBase
from src.models import Procedure
from src.modules.procedure.types import ProcedureInput, ProcedureListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class ProcedureService(CRUDBase[Procedure, ProcedureInput, ProcedureInput]):
    def register(self, inputs: List[ProcedureInput]) -> Response[ProcedureListNode]:
        try:
            result = self.create_or_update('name', inputs, ProcedureListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureListNode(items=[], total_count=0))


ProcedureCrud = ProcedureService(Procedure)
