from __future__ import annotations

from enum import Enum

import strawberry
from typing import List, Optional

from ..theatre_member.types import TheatreMemberNode
from ..theatre_role.types import TheatreRoleNode

@strawberry.enum
class TeamRole(str, Enum):
    SURGEON = "SURGEON"
    ANESTHETIST = "ANESTHETIST"
    SCRUB_NURSE = "SCRUB_NURSE"
    RUNNER_NURSE = "RUNNER_NURSE"


@strawberry.input
class TheatreRecordTeamMemberInput:
    uid: Optional[str] = None
    member_uid: str
    rank: Optional[int] = None
    role: TeamRole

@strawberry.type
class TheatreRecordTeamMemberNode:
    uid: str
    role: TeamRole
    rank: Optional[int]

    @strawberry.field
    def member(self) -> TheatreMemberNode:
        return self.theatre_member


@strawberry.type
class TheatreRecordTeamMemberListNode:
    items: List[TheatreRecordTeamMemberNode]
    total_count: int