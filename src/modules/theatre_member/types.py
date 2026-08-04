import strawberry
from typing import List, Optional


@strawberry.input
class TheatreMemberInput:
    uid: Optional[str] = None
    user_uid: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    pf_number: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None


@strawberry.type
class TheatreMemberNode:
    uid: str
    user_uid: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    pf_number: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]


@strawberry.type
class TheatreMemberListNode:
    items: List[TheatreMemberNode]
    total_count: int


@strawberry.type
class ImportResultNode:
    successful_count: int
    failed_count: int
    failed_records_file: Optional[str] = None
