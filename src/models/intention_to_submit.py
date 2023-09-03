from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date, DateTime
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship

from src.models import BaseModel


class IntentionToSubmit(BaseModel):
    """
    In The Intention of the PostGraduate Student to Submit Their Dissertation
    """
    __tablename__ = "intention_to_submit"
    student_uid: str = Column(String, nullable=False)
    title: str = Column(String, nullable=False, unique=False)
    submission_date = Column(DateTime, nullable=True, unique=False)
    plagiarism_status: str = Column(String, nullable=True, unique=False)
    plagiarism_percentage: float = Column(Float, nullable=True, unique=False)
    plagiarism_report = Column(String, nullable=True, unique=False)
    status: int = Column(Integer, nullable=True, unique=False)
