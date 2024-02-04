from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class SemesterRegistration(BaseModel):
    __tablename__ = "semester_registrations"
    student_uid: str = Column(String, nullable=False)
    study_year: int = Column(Integer, nullable=False)

    # ---------------Mapped Columns ---------------------
    semester_program_id: int = Column(Integer, ForeignKey("program_semesters.id"), nullable=False)
    # semester_program = relationship('ProgramSemester', lazy='subquery', back_populates="semester_registrations")
    semester_program = relationship('ProgramSemester', lazy='subquery')



