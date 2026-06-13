import strawberry
from typing import List, Optional
from ..region.types import RegionNode


@strawberry.input
class ExternalSourceInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None
    region_uid: Optional[str] = None
    region_id: Optional[int] = None


@strawberry.type
class ExternalSourceNode:
    uid: str
    name: str
    code: Optional[str]
    region: Optional[RegionNode]


@strawberry.type
class ExternalSourceListNode:
    items: List[ExternalSourceNode]
    total_count: int