import strawberry
from typing import List, Optional


@strawberry.input
class DeathReasonInput:
    uid: Optional[str] = None
    name: str
    code: Optional[str] = None


@strawberry.type
class DeathReasonNode:
    uid: str
    name: str
    code: Optional[str]


@strawberry.type
class DeathReasonListNode:
    items: List[DeathReasonNode]
    total_count: int
