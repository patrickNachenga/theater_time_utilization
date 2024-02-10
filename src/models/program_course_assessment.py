from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramCourseAssessment(BaseModel):
    __tablename__ = "program_course_assessments"
    minimum_exams: int = Column(Integer, nullable=False, unique=False)
    can_exceed_minimum_by: int = Column(Integer, nullable=True, unique=False)
    maximum_score: int = Column(Integer, nullable=True, unique=False)

    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"),  nullable=False, unique=False)
    # exam_category = relationship('ExamCategory', lazy='subquery', back_populates="program_course_assessments")
    # exam_category = relationship('ExamCategory', lazy='subquery', back_populates="program_course_assessments")
    exam_category = relationship('ExamCategory', lazy='subquery')

    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"),  nullable=False, unique=False)
    # program_course = relationship('ProgramCourse', lazy='subquery', back_populates="program_course_assessments")
    program_course = relationship('ProgramCourse', lazy='subquery')

