from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ExamCoursework(BaseModel):
    __tablename__ = 'exam_coursework'

    student_uid: str = Column(String)
    assessment_number: int = Column(Integer, nullable=False)
    score: float = Column(Float, nullable=False)
    weight: float = Column(Float, nullable=False)
    overall_marks: float = Column(Float, nullable=False)

    # ______________________________Foreign Keys_______________________________________________#

    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)
    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False)

    # ___________________________Relationships__________________________________________________#

    exam_coursework_program_course = relationship("ExamCoursework", lazy="subquery",
                                                  back_populates="program_course_exam_coursework")

    exam_coursework_exam_category = relationship("ExamCoursework", lazy="subquery",
                                                 back_populates="exam_category_exam_coursework")
