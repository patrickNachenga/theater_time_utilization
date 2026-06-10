from sqlalchemy import Column, String, Text
from src.models import BaseModel


class TheatreRole(BaseModel):
    __tablename__ = "theatre_roles"
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)

