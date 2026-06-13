from typing import List
from src.modules import CRUDBase
from src.models import ExternalSource
from src.modules.external_source.types import ExternalSourceInput, ExternalSourceListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.region.service import RegionCrud


class ExternalSourceService(CRUDBase[ExternalSource, ExternalSourceInput, ExternalSourceInput]):
    def register(self, inputs: List[ExternalSourceInput]) -> Response[ExternalSourceListNode]:
        try:
            processed_inputs = []
            for input_obj in inputs:
                new_input_obj = input_obj.copy() # Create a copy to avoid modifying the original input
                if new_input_obj.region_uid:
                    region = RegionCrud.get(new_input_obj.region_uid)
                    if not region:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Region with UID {new_input_obj.region_uid} not found.",
                                        data=ExternalSourceListNode(items=[], total_count=0))
                    new_input_obj.region_id = region.id
                    new_input_obj.region_uid = None  # Clear UID to avoid conflicts
                processed_inputs.append(new_input_obj)

            result = self.create_or_update('name', processed_inputs, ExternalSourceListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ExternalSourceListNode(items=[], total_count=0))


ExternalSourceCrud = ExternalSourceService(ExternalSource)