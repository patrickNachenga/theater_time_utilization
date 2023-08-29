from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentSeminar(BaseModel):
    """
    In every semester a student is registering a particular course from a specific program course
    """
    __tablename__ = "student_seminar"
    student_uid: str = Column(String, nullable=False)
    title: str = Column(String, nullable=False, unique=False)
    seminar_date = Column(Date, nullable=True, unique=False)
    is_pass = Column(Boolean, nullable=True, unique=False)
    seminar_marks = Column(Float, nullable=True, unique=False)

    # ---------------Mapped Columns ---------------------
    seminar_type_id: int = Column(Integer, ForeignKey("seminar_types.id"), nullable=False)
