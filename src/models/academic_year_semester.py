from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class AcademicYearSemester(BaseModel):
    __tablename__ = "academic_year_semesters"
    odd_start_date: DateTime = Column(DateTime, nullable=False, unique=False)
    odd_end_date: DateTime = Column(DateTime, nullable=False, unique=False)
    even_start_date: DateTime = Column(DateTime, nullable=True, unique=False)
    even_end_date: DateTime = Column(DateTime, nullable=True, unique=False)
    exam_start_date: DateTime = Column(DateTime, nullable=True, unique=False)
    exam_ticket_date: DateTime = Column(DateTime, nullable=True, unique=False)
    semester: int = Column(Integer, nullable=False)

    # ___________________________Foreign Keys ____________________________#
    academic_year_id: int = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_year = relationship('AcademicYear', lazy='subquery', back_populates="academic_year_semesters")
