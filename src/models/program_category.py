from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramCategory(BaseModel):
    __tablename__ = "program_categories"
    name: str = Column(String, nullable=False, unique=False)
    short_name: str = Column(String, nullable=True, unique=False)
    programs = relationship('Program', lazy='noload', back_populates="program_category")
    intention_to_submit_requirements = relationship('IntentionToSubmitRequirement', lazy='noload',
                                                   back_populates="program_category")
