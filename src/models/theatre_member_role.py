from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseModel


class TheatreMemberRole(BaseModel):
    __tablename__ = "theatre_member_roles"
    member_uid = Column(UUID(as_uuid=True), ForeignKey('theatre_members.uid'), nullable=False)
    role_uid = Column(UUID(as_uuid=True), ForeignKey('theatre_roles.uid'), nullable=False)

