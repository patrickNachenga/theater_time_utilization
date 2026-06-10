from sqlalchemy import Column, String, Integer
from src.models import BaseModel


class Procedure(BaseModel):
    __tablename__ = "procedures"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)
    estimated_minutes: int = Column(Integer, nullable=True)

