from sqlalchemy import Column, Boolean, String, Integer, Float, Date, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models import BaseModel


class ExamResultSummary(BaseModel):
    __tablename__ = "exam_result_summaries"

    program_course_id: int = Column(Integer, nullable=False, unique=True)
    exam_category_id: int = Column(Integer, nullable=False, unique=False)
    student_uid: str = Column(String, nullable=False, unique=True)
    registration_number: str = Column(String, nullable=False, unique=True)
    student_name: str = Column(String, nullable=False)
    gender: str = Column(CHAR(1), nullable=False)
    course_code: str = Column(String, nullable=False)
    course_name: str = Column(String, nullable=False)
    credit: float = Column(Float, nullable=False)
    grade: str = Column(String, nullable=False, unique=False)
    grade_point: float = Column(Float, nullable=False, unique=False)
    grade_remark: str = Column(String, nullable=False, unique=False)
    publish_status: bool = Column(Boolean, nullable=False)
    publisher: str = Column(String, nullable=False)
    publish_date: Date = Column(Date, default=func.now(), nullable=False)

