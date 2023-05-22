from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class ExamCatGroups(BaseModel):
    __tablename__ = "exam_cat_groups"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, unique=True)
