from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class CourseAllocation(BaseModel):
    __tablename__ = "course_allocation"
    id: int = Column(Integer, primary_key=True, index=True)
    program_course_id: str = Column(String, nullable=False, unique=False)
    staff_id: str = Column(String, nullable=False, unique=False)

