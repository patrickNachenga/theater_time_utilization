from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class CourseLearnOutcome(BaseModel):
    __tablename__ = "course_learn_outcomes"
    learning_outcome: str = Column(String, nullable=True)

    # ---------------Mapped Columns ---------------------
    course_id: int = Column(Integer, ForeignKey('courses.id'),nullable=False)
    course = relationship("Course", lazy="subquery", back_populates="course_learn_outcomes")
