from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class Course(BaseModel):
    __tablename__ = "courses"
    id: int = Column(Integer, primary_key=True, index=True)
    description: str = Column(String, nullable=True, unique=False)
    name: str = Column(String, nullable=False, unique=False)
    code: str = Column(String, nullable=False, unique=False)
    offered: int = Column(Integer, nullable=False, unique=False)
    department_id: str = Column(String, nullable=False, unique=False)