from sqlalchemy import Column, Integer, String, DateTime

from src.models import BaseModel


class ProgramCourseAssessment(BaseModel):
    __tablename__ = "program_course_assessment"
    id: int = Column(Integer, primary_key=True, index=True)
    exam_category_id: int = Column(Integer, nullable=False, unique=False)
    program_course_id: int = Column(Integer, nullable=False, unique=False)
    minimum_exams: int = Column(Integer, nullable=False, unique=False)
    can_exceed_minimum_by: int = Column(Integer, nullable=True, unique=False)
    maximum_score: int = Column(Integer, nullable=True, unique=False)
