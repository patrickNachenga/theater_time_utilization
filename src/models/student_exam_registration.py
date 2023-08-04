from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentExamRegistration(BaseModel):
    __tablename__ = 'student_exam_registrations'



    # ______________________________Foreign Keys__________________________________________________#

    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False)
    student_course_registration_id: int = Column(Integer, ForeignKey("student_course_registrations.id"), nullable=False)

    # _____________________________Relationships___________________________________________________#

    exam_category = relationship("ExamCategory", lazy="subquery",
                                                          back_populates="student_exam_registrations")

    student_course_registrations = relationship("StudentCourseRegistration", lazy="subquery",
                                                            back_populates="student_exam_registration")
