from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class CourseAssessment(BaseModel):
    __tablename__ = "course_assessments"
    id: int = Column(Integer, primary_key=True, index=True)
    minimum_exams: int = Column(Integer, nullable=False, unique=False)
    can_exceed_minimum: int = Column(Integer, nullable=True, unique=False)
    maximum_score: int = Column(Integer, nullable=True, unique=False)
    exam_category_uid: str = Column(String, nullable=False, unique=False)

    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"),  nullable=False, unique=False)
    program_course = relationship('ProgramCourse', lazy='subquery', back_populates="course_assessments")

