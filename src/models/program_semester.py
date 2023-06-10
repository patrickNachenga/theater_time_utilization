from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramSemester(BaseModel):
    __tablename__ = "program_semesters"
    study_year: int = Column(Integer, nullable=False)
    semester: int = Column(Integer, nullable=False)
    core_credits: float = Column(Float(4), nullable=False)
    elective_credits: float = Column(Float(4), nullable=False)

    # ---------------Mapped Columns ---------------------
    academic_year_id: int = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_year = relationship('AcademicYear', lazy='subquery', back_populates="program_semesters")

    program_id: int = Column(Integer, ForeignKey("programs.id"), nullable=False)
    program = relationship('Program', lazy='subquery', back_populates="program_semesters")

    # ---------------Referenced Columns ---------------------
    program_courses = relationship('ProgramCourse', lazy='subquery', back_populates="program_semester")
    semester_registrations = relationship('SemesterRegistration', lazy='subquery', back_populates="semester_program")


