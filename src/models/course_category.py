from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class CourseCategory(BaseModel):
    __tablename__ = "course_category"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, unique=False)
    description: str = Column(String, nullable=False, unique=False)
    