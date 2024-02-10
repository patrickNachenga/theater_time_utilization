from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentManuscript(BaseModel):
    """
    In Model for Registering Student Manuscript for PhD and Master's Students
    """
    __tablename__ = "student_manuscript"
    student_uid: str = Column(String, nullable=False)
    title: str = Column(String, nullable=False, unique=False)
    publication_date = Column(Date, nullable=True, unique=False)
    description: str = Column(String, nullable=True, unique=False)
    status: int = Column(Integer, nullable=True, unique=False)
    publication_status: str = Column(String, nullable=True, unique=False)


