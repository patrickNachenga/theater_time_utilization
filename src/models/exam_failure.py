from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentExamFailure(BaseModel):
    __tablename__ = "student_exam_failures"
    is_attended: bool = Column(Boolean, default=False)
    exam_registration_id: int = Column(Integer, ForeignKey("student_exam_registrations.id"), nullable=False)
    student_exam_registration = relationship('StudentExamRegistration', lazy='subquery', back_populates="exam_failure")
    # failure type 1 is first sitting, 2 probation, 3 third attempt, 4 retake
    type: int = Column(Integer, nullable=False)


    