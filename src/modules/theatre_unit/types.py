import strawberry
from typing import List, Optional


@strawberry.input
class TheatreUnitInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None
    location: Optional[str] = None


@strawberry.type
class TheatreUnitNode:
    uid: str
    name: str
    code: Optional[str]
    location: Optional[str]


@strawberry.type
class TheatreUnitListNode:
    items: List[TheatreUnitNode]
    total_count: int
