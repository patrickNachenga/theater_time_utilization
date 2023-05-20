from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class Group(BaseModel):
    __tablename__ = "groups"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)
    code: str = Column(String, nullable=False, unique=True)
