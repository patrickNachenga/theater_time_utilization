from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramCourseStudentAssessment(BaseModel):
    __tablename__ = "program_course_student_assessments"
    question_no: int = Column(Integer, nullable=False, unique=False)
    answer: str = Column(String, nullable=False, unique=False)
    student_course_registration_id: int = Column(Integer, ForeignKey("student_course_registrations.id"), nullable=False)
    student_course_registration = relationship('StudentCourseRegistration', lazy='subquery')
