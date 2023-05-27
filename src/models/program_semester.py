from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramSemester(BaseModel):
    __tablename__ = "program_semesters"
    id: int = Column(Integer, primary_key=True, index=True, unique=False)
    study_year: int = Column(Integer, nullable=False)
    semester: int = Column(Integer, nullable=False)
    core_credits: float = Column(Float(4), nullable=False)
    elective_credits: float = Column(Float(4), nullable=False)
    created_by: str = Column(String, nullable=True, index=True)

    # ---------------Mapped Columns ---------------------
    academic_year_id: int = Column(Integer, ForeignKey("academic_years.id"), nullable=False, index=True)
    academic_year = relationship('AcademicYear', lazy='subquery', back_populates="program_semesters")

    program_id: int = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    program = relationship('Program', lazy='subquery', back_populates="program_semesters")

    # ---------------Referenced Columns ---------------------
    program_courses = relationship('ProgramCourse', lazy='subquery', back_populates="program_semester")

