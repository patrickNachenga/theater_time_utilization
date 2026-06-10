from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseModel


class TheatreRecordTeamMember(BaseModel):
    __tablename__ = "theatre_record_team_members"
    record_uid = Column(UUID(as_uuid=True), ForeignKey('theatre_time_records.uid'), nullable=False)
    member_uid = Column(UUID(as_uuid=True), ForeignKey('theatre_members.uid'), nullable=False)
    role_uid = Column(UUID(as_uuid=True), ForeignKey('theatre_roles.uid'), nullable=False)

