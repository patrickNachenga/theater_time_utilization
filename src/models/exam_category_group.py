from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ExamCategoryGroup(BaseModel):
    __tablename__ = "exam_category_groups"
    name: str = Column(String, nullable=False, unique=False)

    exam_categories = relationship('ExamCategory', lazy='subquery', back_populates="exam_category_group")
