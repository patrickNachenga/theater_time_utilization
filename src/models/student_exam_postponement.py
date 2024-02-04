import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentExamPostponement(BaseModel):
    __tablename__ = 'student_exam_postponements'

    # ______________________________Foreign Keys__________________________________________________#

    student_course_registration_id: int = Column(Integer, ForeignKey("student_course_registrations.id"), nullable=False)

    # _____________________________Relationships___________________________________________________#
    # failure type 1 is first sitting, 2 probation, 3 third attempt, 4 retake
    type: int = Column(Integer, nullable=False)

    # student_course_registration = relationship("StudentCourseRegistration", lazy="subquery",
    #                                            back_populates="student_exam_postponement")

    student_course_registration = relationship("StudentCourseRegistration", lazy="subquery")
    is_resumed: bool = Column(Boolean, default=False)
    reason: str = Column(String(600), nullable=False)
    approved_at = Column(DateTime, default=datetime.utcnow)
    # user who approved
    approved_uid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
