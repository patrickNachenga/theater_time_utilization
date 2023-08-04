from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentCourseRegistration(BaseModel):
    """
    In every semester a student is registering a particular course from a specific program course
    """
    __tablename__ = "student_course_registrations"
    student_uid: str = Column(String, nullable=False)
    moodle_course_enrollment_status: bool = Column(Boolean, default=False)
    moodle_group_enrollment_status: bool = Column(Boolean, default=False)
    # core is 1,elective is 2
    core_elective: int = Column(Integer, nullable=False)

    # ---------------Mapped Columns ---------------------
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)
    program_course = relationship('ProgramCourse', lazy='subquery', back_populates="student_course_registrations")
    student_exam_registration = relationship("StudentExamRegistration", lazy="subquery",
                                                           back_populates="student_course_registrations")
