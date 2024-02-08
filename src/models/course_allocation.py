from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class CourseAllocation(BaseModel):
    __tablename__ = "course_allocations"
    staff_uid: str = Column(String, nullable=False, unique=False)
    moodle_course_enrollment_status: bool = Column(Boolean, unique=False, default=False)
    moodle_group_enrollment_status: bool = Column(Boolean, unique=False, default=False)
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False, unique=False)
    # program_course = relationship("ProgramCourse", lazy="subquery", back_populates="course_allocations")
    program_course = relationship("ProgramCourse", lazy="subquery")
