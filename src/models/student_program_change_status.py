from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentProgramChangeStatus(BaseModel):
    __tablename__ = "student_program_change_status"
    code: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False, unique=True)


    