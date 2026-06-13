import strawberry
from typing import List, Optional
from ..theatre_member.types import TheatreMemberNode
from ..theatre_role.types import TheatreRoleNode


@strawberry.input
class TheatreMemberRoleInput:
    uid: Optional[str] = None
    member_uid: str
    role_uid: str
    member_id: Optional[int] = None
    role_id: Optional[int] = None


@strawberry.type
class TheatreMemberRoleNode:
    uid: str
    member: TheatreMemberNode
    role: TheatreRoleNode


@strawberry.type
class TheatreMemberRoleListNode:
    items: List[TheatreMemberRoleNode]
    total_count: int