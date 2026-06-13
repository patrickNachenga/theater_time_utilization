from typing import List
from src.modules import CRUDBase
from src.models import TheatreRecordTeamMember
from src.modules.theatre_record_team_member.types import TheatreRecordTeamMemberInput, TheatreRecordTeamMemberListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.theatre_procedure_record.service import TheatreTimeRecordCrud
from src.modules.theatre_member.service import TheatreMemberCrud
from src.modules.theatre_role.service import TheatreRoleCrud


class TheatreRecordTeamMemberService(CRUDBase[TheatreRecordTeamMember, TheatreRecordTeamMemberInput, TheatreRecordTeamMemberInput]):
    def register(self, inputs: List[TheatreRecordTeamMemberInput]) -> Response[TheatreRecordTeamMemberListNode]:
        try:
            processed_inputs = []
            for input_obj in inputs:
                new_input_obj = input_obj.copy() # Create a copy to avoid modifying the original input

                if new_input_obj.record_uid:
                    record = TheatreTimeRecordCrud.get(new_input_obj.record_uid)
                    if not record:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Theatre Record with UID {new_input_obj.record_uid} not found.",
                                        data=TheatreRecordTeamMemberListNode(items=[], total_count=0))
                    new_input_obj.record_id = record.id
                    new_input_obj.record_uid = None

                if new_input_obj.member_uid:
                    member = TheatreMemberCrud.get(new_input_obj.member_uid)
                    if not member:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Theatre Member with UID {new_input_obj.member_uid} not found.",
                                        data=TheatreRecordTeamMemberListNode(items=[], total_count=0))
                    new_input_obj.member_id = member.id
                    new_input_obj.member_uid = None

                if new_input_obj.role_uid:
                    role = TheatreRoleCrud.get(new_input_obj.role_uid)
                    if not role:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Theatre Role with UID {new_input_obj.role_uid} not found.",
                                        data=TheatreRecordTeamMemberListNode(items=[], total_count=0))
                    new_input_obj.role_id = role.id
                    new_input_obj.role_uid = None

                processed_inputs.append(new_input_obj)

            # Assuming 'record_id' is a suitable unique field for update checks within the CRUDBase.
            # If uniqueness is based on a combination of fields (e.g., record_id, member_id, role_id),
            # the CRUDBase's create_or_update method might need further customization or a different unique_field.
            result = self.create_or_update('record_id', processed_inputs, TheatreRecordTeamMemberListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreRecordTeamMemberListNode(items=[], total_count=0))


TheatreRecordTeamMemberCrud = TheatreRecordTeamMemberService(TheatreRecordTeamMember)