from typing import List
from src.modules import CRUDBase
from src.models import TheatreMember
from src.modules.theatre_member.types import TheatreMemberInput, TheatreMemberListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreMemberService(CRUDBase[TheatreMember, TheatreMemberInput, TheatreMemberInput]):
    def register(self, inputs: List[TheatreMemberInput]) -> Response[TheatreMemberListNode]:
        try:
            result = self.create_or_update('pf_number', inputs, TheatreMemberListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))


TheatreMemberCrud = TheatreMemberService(TheatreMember)
