from sqlalchemy import Column, String
from src.models import BaseModel


class InternalSource(BaseModel):
    __tablename__ = "internal_sources"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)

