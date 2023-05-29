from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramCategory(BaseModel):
    __tablename__ = "program_categories"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, unique=False)
    short_name: str = Column(String, nullable=True, unique=False)
    programs = relationship('Program', lazy='subquery', back_populates="program_category")

