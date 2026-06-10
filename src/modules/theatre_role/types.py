import strawberry
from typing import List, Optional


@strawberry.input
class TheatreRoleInput:
    uid: Optional[str] = None
    name: str
    description: Optional[str] = None


@strawberry.type
class TheatreRoleNode:
    uid: str
    name: str
    description: Optional[str]


@strawberry.type
class TheatreRoleListNode:
    items: List[TheatreRoleNode]
    total_count: int
