from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class SeminarTypes(BaseModel):
    __tablename__ = "seminar_types"
    name: str = Column(String, nullable=False, unique=False)
    description: str = Column(String, nullable=False, unique=False)
    rank: str = Column(Integer, nullable=False, unique=False)


    