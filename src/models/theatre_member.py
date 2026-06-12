from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseModel


class TheatreMember(BaseModel):
    __tablename__ = "theatre_members"
    user_uid = Column(UUID(as_uuid=True), nullable=False)
    first_name: str = Column(String(255), nullable=False)
    middle_name: str = Column(String(255), nullable=False)
    last_name: str = Column(String(255), nullable=False)
    pf_number: str = Column(String(50), nullable=False,  index=True)

