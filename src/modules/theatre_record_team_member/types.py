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
    record_uid: str
    member_uid: str
    role: TeamRole

@strawberry.type
class TheatreRecordTeamMemberNode:
    uid: str
    member: TheatreMemberNode
    role: TeamRole


@strawberry.type
class TheatreRecordTeamMemberListNode:
    items: List[TheatreRecordTeamMemberNode]
    total_count: int