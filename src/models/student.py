from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class Student(BaseModel):
    __tablename__ = "students"
    id: int = Column(Integer, primary_key=True, index=True)
    reg_no: str = Column(String, nullable=False, unique=True)


