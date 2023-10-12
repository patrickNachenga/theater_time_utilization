from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentPostponementApprovalStatus(BaseModel):
    __tablename__ = "student_postponement_approval_status"
    code: str = Column(String, nullable=False, unique=True)
    description: str = Column(String, nullable=False, unique=True)

    # ---------------Referenced Columns ---------------------
    student_study_postponements = relationship('StudentStudyPostponement', lazy='subquery',
                                               back_populates="student_postponement_approval_status")
