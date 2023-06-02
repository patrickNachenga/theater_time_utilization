from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class Course(BaseModel):
    __tablename__ = "courses"
    description: str = Column(String, nullable=True, unique=False)
    name: str = Column(String, nullable=False, unique=False)
    code: str = Column(String, nullable=False, unique=False)
    offered: int = Column(Integer, nullable=False, unique=False)
    moodle_id: str = Column(String, nullable=True)

    # ---------------Mapped Columns ---------------------
    department_uid: str = Column(String, nullable=False, unique=False)

    # ---------------Referenced Columns ---------------------
    program_courses = relationship('ProgramCourse', lazy='subquery', back_populates="course")
