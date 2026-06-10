import strawberry
from typing import List, Optional


@strawberry.input
class RegionInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None


@strawberry.type
class RegionNode:
    uid: str
    name: str
    code: Optional[str]


@strawberry.type
class RegionListNode:
    items: List[RegionNode]
    total_count: int
