from sqlalchemy import Column, Integer, String

from src.models import BaseModel

class Course(BaseModel):
    __tablename__ = "course"
    id: int = Column(Integer, primary_key=True, index=True)
    description: str = Column(String, nullable=True, unique=True)
    name: str = Column(String, nullable=True)
    code: str = Column(String, nullable=False, unique=True)


