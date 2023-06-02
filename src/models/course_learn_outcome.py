from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class CourseLearnOutcome(BaseModel):
    __tablename__ = "course_learn_outcomes"
    staff_uid: str = Column(String, nullable=False)
    learning_outcome: str = Column(String, nullable=True)

    # ---------------Mapped Columns ---------------------
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)
    program_course = relationship('ProgramCourse', lazy='subquery', back_populates="course_learn_outcomes")






