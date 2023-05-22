from sqlalchemy import Column, Integer, String

from src.models import BaseModel

class ExamCats(BaseModel):
    __tablename__ = "exam_cats"
    id: int = Column(Integer, primary_key=True, index=True)
    code: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False, unique=True)
    exam_group_id: int = Column(String, nullable=False, unique=False)