from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ByLaw(BaseModel):
    __tablename__ = "by_laws"
    name: str = Column(String, nullable=False, unique=True)
    code: str = Column(String, nullable=False, unique=True)
    status: bool = Column(Boolean, nullable=False, default=False)
    start_date: DateTime = Column(DateTime, nullable=True, unique=False)
    end_date: DateTime = Column(DateTime, nullable=True, unique=False)


