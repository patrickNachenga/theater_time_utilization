from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentPostponementReason(BaseModel):
    __tablename__ = "student_postponement_reasons"
    reason = Column(String, nullable=False)
    descriptions = Column(String, nullable=False)

    # ---------------Referenced Columns ---------------------
    student_study_postponements = relationship('StudentStudyPostponement', lazy='subquery', back_populates="student_postponement_reason")
