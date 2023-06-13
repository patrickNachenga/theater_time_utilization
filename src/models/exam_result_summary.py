from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models import BaseModel


class ExamResultSummary(BaseModel):
    __tablename__ = "exam_result_summaries"

    student_uid: str = Column(String, nullable=False, unique=True)
    grade: str = Column(String, nullable=False, unique=False)
    grade_point: float = Column(Float, nullable=False, unique=False)
    grade_remark: str = Column(String, nullable=False, unique=False)
    publish_status: bool = Column(Boolean, nullable=False)
    publisher: str = Column(String, nullable=False)
    publish_date: Date = Column(Date, default=func.now(), nullable=False)

    # _________________________Foreign Keys________________________________________________#

    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)
    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False)

    # __________________________Relationships_______________________________________________#

    program_course_exam_result_summary = relationship("ProgramCourse", lazy="subquery",
                                                      back_populates="exam_result_summary")

    exam_category_exam_result_summary = relationship("ExamCategory", lazy="subquery",
                                                     back_populates="exam_result_summary")
