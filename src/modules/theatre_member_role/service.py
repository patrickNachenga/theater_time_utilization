from typing import List, Optional

from src.core.security import Info
from src.database.session import session_scope
from src.modules import CRUDBase
from src.models import TheatreMemberRole
from src.modules.theatre_member_role.types import TheatreMemberRoleInput, TheatreMemberRoleListNode
from src.modules.theatre_member.service import TheatreMemberCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreMemberRoleService(CRUDBase[TheatreMemberRole, TheatreMemberRoleInput, TheatreMemberRoleInput]):
    def register(self, inputs: List[TheatreMemberRoleInput], info: Optional[Info] = None) -> Response[TheatreMemberRoleListNode]:
        """
        Assigns one or more roles to theatre members. A member can hold
        several roles at once, so this inserts a new (member, role) mapping
        rather than upserting on member alone — re-assigning a role a member
        already has is a no-op instead of an error.
        """
        try:
            username = self._get_user_name(info)
            seen_in_batch = set()

            with session_scope() as session:
                for input_obj in inputs:
                    member = TheatreMemberCrud.get(input_obj.member_uid)
                    if not member:
                        return Response(
                            status=False,
                            code=ResponseCode.VALIDATION_ERROR,
                            message=f"Theatre Member with UID {input_obj.member_uid} not found.",
                            data=TheatreMemberRoleListNode(items=[], total_count=0),
                        )

                    # The session has autoflush disabled, so a not-yet-flushed insert added
                    # earlier in this same batch is invisible to this query - a repeated
                    # member+role pair within one call would otherwise be inserted twice and
                    # hit the DB's unique constraint, rolling back the whole batch.
                    batch_key = (member.id, input_obj.role)
                    if batch_key in seen_in_batch:
                        continue
                    seen_in_batch.add(batch_key)

                    existing = (
                        session.query(TheatreMemberRole)
                        .filter(
                            TheatreMemberRole.member_id == member.id,
                            TheatreMemberRole.role == input_obj.role,
                            TheatreMemberRole.deleted_at.is_(None),
                        )
                        .first()
                    )
                    if existing:
                        continue

                    mapping = TheatreMemberRole(member_id=member.id, role=input_obj.role)
                    if username:
                        mapping.created_by = username
                        mapping.updated_by = username
                    session.add(mapping)

                session.commit()

            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Role(s) assigned successfully",
                data=TheatreMemberRoleListNode(items=[], total_count=0),
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to assign role(s)",
                data=TheatreMemberRoleListNode(items=[], total_count=0),
            )


TheatreMemberRoleCrud = TheatreMemberRoleService(TheatreMemberRole)
