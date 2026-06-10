from typing import List
from src.modules import CRUDBase
from src.models import TheatreRecordTeamMember
from src.modules.theatre_record_team_member.types import TheatreRecordTeamMemberInput, TheatreRecordTeamMemberListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreRecordTeamMemberService(CRUDBase[TheatreRecordTeamMember, TheatreRecordTeamMemberInput, TheatreRecordTeamMemberInput]):
    def register(self, inputs: List[TheatreRecordTeamMemberInput]) -> Response[TheatreRecordTeamMemberListNode]:
        try:
            result = self.create_or_update('record_uid', inputs, TheatreRecordTeamMemberListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordTeamMemberListNode(items=[], total_count=0))


TheatreRecordTeamMemberCrud = TheatreRecordTeamMemberService(TheatreRecordTeamMember)
