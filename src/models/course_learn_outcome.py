from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class CourseLearnOutcome(BaseModel):
    __tablename__ = "course_learn_outcome"
    id: int = Column(Integer, primary_key=True, index=True)
    staff_id: str = Column(String, nullable=False, index=True)
    program_course_id: str = Column(String, nullable=False, index=True)
    learning_outcome: str = Column(String, nullable=True)






