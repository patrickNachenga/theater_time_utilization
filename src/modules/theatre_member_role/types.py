from enum import Enum

import strawberry
from typing import List, Optional

from ..theatre_member.types import TheatreMemberNode


@strawberry.enum
class MemberRole(str, Enum):
    SURGEONS = "SURGEONS"
    ANAESTHETISTS = "ANAESTHETISTS"
    NURSES = "NURSES"


@strawberry.input
class TheatreMemberRoleInput:
    uid: Optional[str] = None
    member_uid: str
    role: MemberRole


@strawberry.type
class TheatreMemberRoleNode:
    uid: str
    role: MemberRole

    @strawberry.field
    def member(self) -> TheatreMemberNode:
        return self.theatre_member


@strawberry.type
class TheatreMemberRoleListNode:
    items: List[TheatreMemberRoleNode]
    total_count: int
