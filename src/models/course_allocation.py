from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class CourseAllocation(BaseModel):
    __tablename__ = "course_allocations"
    id: int = Column(Integer, primary_key=True, index=True)
    staff_uid: str = Column(String, nullable=False, unique=False)
    program_course_id: str = Column(String, ForeignKey("program_courses.id"), nullable=False, unique=False)
    program_course = relationship("ProgramCourse", lazy="subquery", back_populates="course_allocations")
