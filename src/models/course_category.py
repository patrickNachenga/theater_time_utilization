from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class CourseCategory(BaseModel):
    __tablename__ = "course_categories"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, unique=False)
    description: str = Column(String, nullable=False, unique=False)
    program_courses = relationship('ProgramCourse', lazy='subquery', back_populates="course_category")


    