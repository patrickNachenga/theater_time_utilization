from typing import List
from src.modules import CRUDBase
from src.models import ExternalSource
from src.modules.external_source.types import ExternalSourceInput, ExternalSourceListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class ExternalSourceService(CRUDBase[ExternalSource, ExternalSourceInput, ExternalSourceInput]):
    def register(self, inputs: List[ExternalSourceInput]) -> Response[ExternalSourceListNode]:
        try:
            result = self.create_or_update('name', inputs, ExternalSourceListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ExternalSourceListNode(items=[], total_count=0))


ExternalSourceCrud = ExternalSourceService(ExternalSource)
