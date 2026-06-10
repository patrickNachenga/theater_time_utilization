import strawberry
from typing import List, Optional


@strawberry.input
class ExternalSourceInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None
    region_uid: Optional[str] = None


@strawberry.type
class ExternalSourceNode:
    uid: str
    name: str
    code: Optional[str]
    region_uid: Optional[str]


@strawberry.type
class ExternalSourceListNode:
    items: List[ExternalSourceNode]
    total_count: int
