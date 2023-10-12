from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentStudyPostponement(BaseModel):
    __tablename__ = "student_study_postponements"

    description = Column(String, nullable=False)
    attached_file_url = Column(String, nullable=False)
    approval_status = Column(String, nullable=False)
    student_uid = Column(String, nullable=False)

    # ___________________________Foreign Keys ____________________________#
    reason_id: int = Column(Integer, ForeignKey("student_study_postponement.id"), nullable=False)
    student_postponement_reason = relationship('StudentPostponementReason', lazy='subquery', back_populates="student_study_postponements")

    approval_status_id: int = Column(Integer, ForeignKey("student_study_postponement.id"), nullable=False)
    student_postponement_approval_status = relationship('StudentPostponementApprovalStatus', lazy='subquery', back_populates="student_study_postponements")


