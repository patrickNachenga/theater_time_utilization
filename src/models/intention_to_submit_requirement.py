from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class IntentionToSubmitRequirement(BaseModel):
    __tablename__ = "intention_to_submit_requirements"
    minimum_manuscripts: int = Column(Integer, nullable=False)
    minimum_seminars: int = Column(Integer, nullable=False)
    seminar_pass_marks: float = Column(Integer, nullable=False)
    life_span: int = Column(Integer, nullable=False)

    # ---------------Mapped Columns ---------------------
    program_category_id: int = Column(Integer, ForeignKey("program_categories.id"), nullable=False)
    program_category = relationship('ProgramCategory', lazy='subquery', back_populates="intention_to_submit_requirements")


