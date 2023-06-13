from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models import BaseModel


class ExamResultSummary(BaseModel):
    __tablename__ = "exam_results"
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)
    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False)
    student_uid: str = Column(String, nullable=False, unique=True)
    grade: str = Column(String, nullable=False, unique=False)
    grade_point: float = Column(Float, nullable=False, unique=False)
    grade_remark: str = Column(String, nullable=False, unique=False)
    publish_status: bool = Column(Boolean, nullable=False)
    publisher: str = Column(String, nullable=False)
    publish_date: Date = Column(Date, default=func.now(), nullable=False)

    exam_result_summary_program_course = relationship("ExamResultSummary", lazy="subquery",
                                                      back_populates="program_course_exam_result_summary")

    exam_result_summary_exam_category = relationship("ExamResultSummary", lazy="subquery",
                                                     back_populates="exam_category_exam_result_summary")

