from sqlalchemy import Column, String
from src.models import BaseModel


class Region(BaseModel):
    __tablename__ = "regions"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)

