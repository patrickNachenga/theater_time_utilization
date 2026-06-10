from typing import List
from src.modules import CRUDBase
from src.models import TheatreMemberRole
from src.modules.theatre_member_role.types import TheatreMemberRoleInput, TheatreMemberRoleListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreMemberRoleService(CRUDBase[TheatreMemberRole, TheatreMemberRoleInput, TheatreMemberRoleInput]):
    def register(self, inputs: List[TheatreMemberRoleInput]) -> Response[TheatreMemberRoleListNode]:
        try:
            result = self.create_or_update('member_uid', inputs, TheatreMemberRoleListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberRoleListNode(items=[], total_count=0))


TheatreMemberRoleCrud = TheatreMemberRoleService(TheatreMemberRole)
