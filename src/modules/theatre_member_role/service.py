from typing import List
from src.modules import CRUDBase
from src.models import TheatreMemberRole
from src.modules.theatre_member_role.types import TheatreMemberRoleInput, TheatreMemberRoleListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.theatre_member.service import TheatreMemberCrud
from src.modules.theatre_role.service import TheatreRoleCrud


class TheatreMemberRoleService(CRUDBase[TheatreMemberRole, TheatreMemberRoleInput, TheatreMemberRoleInput]):
    def register(self, inputs: List[TheatreMemberRoleInput]) -> Response[TheatreMemberRoleListNode]:
        try:
            processed_inputs = []
            for input_obj in inputs:
                new_input_obj = input_obj.copy() # Create a copy to avoid modifying the original input

                if new_input_obj.member_uid:
                    member = TheatreMemberCrud.get(new_input_obj.member_uid)
                    if not member:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Theatre Member with UID {new_input_obj.member_uid} not found.",
                                        data=TheatreMemberRoleListNode(items=[], total_count=0))
                    new_input_obj.member_id = member.id
                    new_input_obj.member_uid = None  # Clear UID to avoid conflicts

                if new_input_obj.role_uid:
                    role = TheatreRoleCrud.get(new_input_obj.role_uid)
                    if not role:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Theatre Role with UID {new_input_obj.role_uid} not found.",
                                        data=TheatreMemberRoleListNode(items=[], total_count=0))
                    new_input_obj.role_id = role.id
                    new_input_obj.role_uid = None  # Clear UID to avoid conflicts

                processed_inputs.append(new_input_obj)

            result = self.create_or_update('member_id', processed_inputs, TheatreMemberRoleListNode) # Changed unique field to member_id
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberRoleListNode(items=[], total_count=0))


TheatreMemberRoleCrud = TheatreMemberRoleService(TheatreMemberRole)