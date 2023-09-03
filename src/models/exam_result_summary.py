from sqlalchemy import Column, Boolean, String, Integer, Float, Date, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models import BaseModel


class ExamResultSummary(BaseModel):
    __tablename__ = "exam_result_summaries"

    program_course_id: int = Column(Integer, nullable=False)
    student_uid: str = Column(String, nullable=False)
    registration_number: str = Column(String, nullable=False)
    first_name: str = Column(String, nullable=False)
    middle_name: str = Column(String, nullable=True)
    last_name: str = Column(String, nullable=False)
    gender: str = Column(String, nullable=False)
    course_code: str = Column(String, nullable=False)
    course_name: str = Column(String, nullable=False)
    cw_practical: float = Column(Float, nullable=True, unique=False)
    cw_theory: float = Column(Float, nullable=True, unique=False)
    cw_score: float = Column(Float, nullable=True, unique=False)
    ue_practical: float = Column(Float, nullable=True, unique=False)
    ue_theory: float = Column(Float, nullable=True, unique=False)
    ue_score: float = Column(Float, nullable=True, unique=False)
    total_score: float = Column(Float, nullable=True, unique=False)
    credit: float = Column(Float, nullable=True)
    grade: str = Column(String, nullable=True, unique=False)
    grade_point_credit: float = Column(Float, nullable=True, unique=False)
    grade_point: float = Column(Float, nullable=True, unique=False)
    grade_remark: str = Column(String, nullable=True, unique=False)
    number_of_sitting: int = Column(Integer, default =1, unique=False)
    exam_status: int = Column(Boolean, nullable=True)
    publish_status: int = Column(Boolean, nullable=True)
    publisher: str = Column(String, nullable=True)
    publish_date: Date = Column(Date, nullable=True)
    study_year: int = Column(Integer, nullable=False)
    semester: int = Column(Integer, nullable=False)
    academic_year_id: int = Column(Integer, nullable=False)



