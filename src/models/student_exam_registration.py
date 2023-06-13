from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentExamRegistration(BaseModel):
    __tablename__ = 'student_exam_registrations'

    student_uid: str = Column(String, nullable=False)

    # ______________________________Foreign Keys__________________________________________________#

    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False)
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)

    # _____________________________Relationships___________________________________________________#

    exam_category = relationship("ExamCategory", lazy="subquery",
                                                          back_populates="student_exam_registrations")

    program_course = relationship("ProgramCourse", lazy="subquery",
                                                            back_populates="student_exam_registrations")
