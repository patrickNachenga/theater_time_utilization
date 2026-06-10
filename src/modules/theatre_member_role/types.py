import strawberry
from typing import List, Optional


@strawberry.input
class TheatreMemberRoleInput:
    uid: Optional[str] = None
    member_uid: str
    role_uid: str


@strawberry.type
class TheatreMemberRoleNode:
    uid: str
    member_uid: str
    role_uid: str


@strawberry.type
class TheatreMemberRoleListNode:
    items: List[TheatreMemberRoleNode]
    total_count: int
