import strawberry
from typing import List


@strawberry.input
class TheatreRecordTeamMemberInput:
    uid: str = None
    record_uid: str
    member_uid: str
    role_uid: str


@strawberry.type
class TheatreRecordTeamMemberNode:
    uid: str
    record_uid: str
    member_uid: str
    role_uid: str


@strawberry.type
class TheatreRecordTeamMemberListNode:
    items: List[TheatreRecordTeamMemberNode]
    total_count: int
