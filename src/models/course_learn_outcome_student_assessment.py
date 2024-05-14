from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from src.models import BaseModel


class CourseLearnOutcomeStudentAssessments(BaseModel):
    __tablename__ = "course_learn_outcome_student_assessments"
    answer: int = Column(Integer, nullable=False, unique=False)
    # answer: str = Column(String, nullable=False, unique=False)
    student_course_registration_id: int = Column(Integer, ForeignKey("student_course_registrations.id"), nullable=False)
    student_course_registration = relationship('StudentCourseRegistration', lazy='subquery')
    course_learn_outcome_id: int = Column(Integer, ForeignKey("course_learn_outcomes.id"), nullable=False)
    course_learn_outcome = relationship('CourseLearnOutcome', lazy='subquery')
