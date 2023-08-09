from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentExamRegistration(BaseModel):
    __tablename__ = 'student_exam_registrations'

    # ______________________________Foreign Keys__________________________________________________#

    student_course_registration_id: int = Column(Integer, ForeignKey("student_course_registrations.id"), nullable=False)

    # _____________________________Relationships___________________________________________________#


    # failure type 1 is first sitting, 2 probation, 3 third attempt, 4 retake
    type: int = Column(Integer, nullable=False)

    student_course_registration = relationship("StudentCourseRegistration", lazy="subquery",
                                                back_populates="student_exam_registration")
    exam_failure = relationship("StudentExamFailure", lazy="subquery",
                                back_populates="student_exam_registration")
