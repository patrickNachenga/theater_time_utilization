import strawberry
from typing import List, Optional
from enum import Enum

from ..theatre_unit.types import TheatreUnitNode


@strawberry.enum
class TheatreRoomStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@strawberry.input
class TheatreRoomInput:
    uid: Optional[str] = None
    theatre_unit_uid: str = ""
    name: str = ""
    code: Optional[str] = None
    category: Optional[str] = None
    capacity: Optional[int] = None
    equipment_notes: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TheatreRoomStatus] = None


@strawberry.type
class TheatreRoomNode:
    uid: str
    theatre_unit: Optional[TheatreUnitNode]
    name: str
    code: Optional[str]
    category: Optional[str]
    capacity: Optional[int]
    equipment_notes: Optional[str]
    description: Optional[str]
    status: TheatreRoomStatus


@strawberry.type
class TheatreRoomListNode:
    items: List[TheatreRoomNode]
    total_count: int
