from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramCapacity(BaseModel):
    __tablename__ = "program_capacities"

    capacity: int = Column(Integer, nullable=False)
    program_id: int = Column(Integer, ForeignKey("programs.id"))
    program = relationship('Program', lazy='subquery', back_populates="program_capacities")
    academic_year_id: int = Column(Integer, ForeignKey("academic_years.id"),nullable=False)
    academic_year = relationship('AcademicYear', lazy='subquery', back_populates="program_capacities")
    is_active = Column(Boolean)
