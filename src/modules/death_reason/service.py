from typing import List
from src.modules import CRUDBase
from src.models import DeathReason
from src.modules.death_reason.types import DeathReasonInput, DeathReasonListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class DeathReasonService(CRUDBase[DeathReason, DeathReasonInput, DeathReasonInput]):
    def register(self, inputs: List[DeathReasonInput]) -> Response[DeathReasonListNode]:
        try:
            result = self.create_or_update('name', inputs, DeathReasonListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=DeathReasonListNode(items=[], total_count=0))


DeathReasonCrud = DeathReasonService(DeathReason)
