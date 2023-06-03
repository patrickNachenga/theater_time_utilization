from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class Student(BaseModel):
    __tablename__ = "students"
    reg_no: str = Column(String, nullable=False, unique=False)


