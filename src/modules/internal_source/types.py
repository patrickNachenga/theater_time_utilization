import strawberry
from typing import List, Optional


@strawberry.input
class InternalSourceInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None


@strawberry.type
class InternalSourceNode:
    uid: str
    name: str
    code: Optional[str]


@strawberry.type
class InternalSourceListNode:
    items: List[InternalSourceNode]
    total_count: int
