from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ExamCourseResultForwardLogs(BaseModel):
    __tablename__ = "exam_course_result_forward_logs"
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False, unique=False)
    staff_name: str = Column(String, nullable=False, unique=False)
    staff_uid: str = Column(String, nullable=False, unique=False)
    forwarded_from: int = Column(Integer, default=False)
    forwarded_to: int = Column(Integer, default=False)
    program_course = relationship("ProgramCourse", lazy="subquery")
