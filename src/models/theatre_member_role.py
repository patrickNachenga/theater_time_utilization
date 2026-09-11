from enum import Enum

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.models import BaseModel


class MemberRole(str, Enum):
    SURGEONS = "SURGEONS"
    ANAESTHETISTS = "ANAESTHETISTS"
    NURSES = "NURSES"


class TheatreMemberRole(BaseModel):
    """
    Tags a theatre member with a role they are qualified for (a roster-level
    qualification), independent of the per-procedure team slot they end up
    filling (see TheatreRecordTeamMember.role / TeamRole for that). A member
    may hold multiple roles at once — e.g. a member tagged NURSES is eligible
    for both the Scrub Nurse and Runner Nurse slots on the procedure form.
    """
    __tablename__ = "theatre_member_roles"
    __table_args__ = (UniqueConstraint("member_id", "role", name="uq_theatre_member_id_role"),)

    member_id = Column(ForeignKey("theatre_members.id"), nullable=False, index=True)
    role = Column(SQLEnum(MemberRole), nullable=False, index=True)

    theatre_member = relationship("TheatreMember")
