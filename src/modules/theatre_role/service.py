from typing import List
from src.modules import CRUDBase
from src.models import TheatreRole
from src.modules.theatre_role.types import TheatreRoleInput, TheatreRoleListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreRoleService(CRUDBase[TheatreRole, TheatreRoleInput, TheatreRoleInput]):
    def register(self, inputs: List[TheatreRoleInput]) -> Response[TheatreRoleListNode]:
        try:
            result = self.create_or_update('name', inputs, TheatreRoleListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRoleListNode(items=[], total_count=0))


TheatreRoleCrud = TheatreRoleService(TheatreRole)
