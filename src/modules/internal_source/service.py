from typing import List
from src.modules import CRUDBase
from src.models import InternalSource
from src.modules.internal_source.types import InternalSourceInput, InternalSourceListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class InternalSourceService(CRUDBase[InternalSource, InternalSourceInput, InternalSourceInput]):
    def register(self, inputs: List[InternalSourceInput]) -> Response[InternalSourceListNode]:
        try:
            result = self.create_or_update('name', inputs, InternalSourceListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=InternalSourceListNode(items=[], total_count=0))


InternalSourceCrud = InternalSourceService(InternalSource)
