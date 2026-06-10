from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseModel


class TheatreMember(BaseModel):
    __tablename__ = "theatre_members"
    user_uid = Column(UUID(as_uuid=True), nullable=True)
    first_name: str = Column(String(255), nullable=True)
    middle_name: str = Column(String(255), nullable=True)
    last_name: str = Column(String(255), nullable=True)
    pf_number: str = Column(String(50), nullable=True)

