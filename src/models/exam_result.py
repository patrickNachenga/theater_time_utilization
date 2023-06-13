from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from src.models import BaseModel


class ExamResult(BaseModel):
    __tablename__ = "exam_results"
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False, unique=False)
    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False, unique=False)
    student_uid: int = Column(Integer, nullable=False, unique=False)
    score: float = Column(Float, nullable=False, unique=False)
    out_of: float = Column(Float, nullable=False, unique=False)
    weight: int = Column(Integer, nullable=False, unique=False)
    overall_marks: float = Column(Integer, nullable=False)

    exam_result_program_course = relationship("ExamResult", lazy="subquery", back_populates="program_course_exam_result")

    exam_result_exam_category = relationship("ExamResult", lazy="subquery", back_populates="exam_category_exam_result")

