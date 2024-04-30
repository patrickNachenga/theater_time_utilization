from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from src.models import BaseModel


class TeachingAndContinuousCourseAssessmentResult(BaseModel):
    __tablename__ = "teaching_and_continuous_course_assessment_results"
    answer: str = Column(String, nullable=False, unique=False)
    assessment_id: int = Column(Integer, nullable=False, unique=False)
    student_course_registration_id: int = Column(Integer, ForeignKey("student_course_registrations.id"), nullable=False)
    student_course_registration = relationship('StudentCourseRegistration', lazy='subquery')
