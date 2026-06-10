from typing import List
from src.modules import CRUDBase
from src.models import ProcedureDelayCategory
from src.modules.procedure_delay_category.types import ProcedureDelayCategoryInput, ProcedureDelayCategoryListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class ProcedureDelayCategoryService(CRUDBase[ProcedureDelayCategory, ProcedureDelayCategoryInput, ProcedureDelayCategoryInput]):
    def register(self, inputs: List[ProcedureDelayCategoryInput]) -> Response[ProcedureDelayCategoryListNode]:
        try:
            result = self.create_or_update('name', inputs, ProcedureDelayCategoryListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCategoryListNode(items=[], total_count=0))


ProcedureDelayCategoryCrud = ProcedureDelayCategoryService(ProcedureDelayCategory)
