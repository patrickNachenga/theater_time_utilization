from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ExamCategories(BaseModel):
    __tablename__ = "exam_categories"
    code: str = Column(String, nullable=False, unique=False)
    name: str = Column(String, nullable=False, unique=False)
    exam_category_group_id: int = Column(Integer, ForeignKey("exam_category_groups.id"), nullable=False)

    exam_category_group = relationship('ExamCategoryGroup', lazy='subquery', back_populates="exam_categories")