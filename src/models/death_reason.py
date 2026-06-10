from sqlalchemy import Column, String
from src.models import BaseModel


class DeathReason(BaseModel):
    __tablename__ = "death_reasons"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)

