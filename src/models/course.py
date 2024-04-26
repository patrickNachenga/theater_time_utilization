from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class Course(BaseModel):
    __tablename__ = "courses"
    description: str = Column(String, nullable=True, unique=False)
    name: str = Column(String, nullable=False, unique=False)
    code: str = Column(String, nullable=False, unique=False)
    offered: int = Column(Integer, nullable=False, unique=False)
    moodle_id: str = Column(String, nullable=True)
    moodle_check_status: bool = Column(Boolean, unique=False, default=False)
    # ---------------Mapped Columns ---------------------
    department_uid: str = Column(String, nullable=False, unique=False)

    # ---------------Referenced Columns ---------------------
    # program_courses = relationship('ProgramCourse', lazy='subquery', back_populates="course")
    # course_learn_outcomes = relationship("CourseLearnOutcome", lazy="subquery", back_populates="course")
