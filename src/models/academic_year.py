from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from src.models import BaseModel


class AcademicYear(BaseModel):
    __tablename__ = "academic_years"
    name: str = Column(String, nullable=False, unique=False)
    status: int = Column(Integer, nullable=False, unique=False)
    start_date: DateTime = Column(DateTime, nullable=True, unique=False)
    end_date: DateTime = Column(DateTime, nullable=True, unique=False)

    program_semesters = relationship('ProgramSemester', lazy='subquery', back_populates="academic_year")
    program_capacities = relationship('ProgramCapacity', lazy='subquery', back_populates="program")
