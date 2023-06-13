from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentExamRegistration(BaseModel):
    __tablename__ = 'student_exam_registrations'

    student_uid: int = Column(Integer, nullable=False)
    course_id: int = Column(Integer, nullable=False)

    # ______________________________Foreign Keys__________________________________________________#

    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False)
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)

    # _____________________________Relationships___________________________________________________#

    student_exam_registration_exam_category = relationship("StudentExamRegistration", lazy="subquery",
                                                           back_populates="exam_category_student_exam_registration")

    student_exam_registration_program_course = relationship("StudentExamRegistration", lazy="subquery",
                                                            back_populates="program_course_student_exam_registration")
    program_course_student_exam_registration = relationship("StudentExamRegistration", lazy="subquery",
                                                            back_populates="student_exam_registration_program_course")
