from sqlalchemy import Column, Integer, String, Float, ForeignKey

from src.models import BaseModel


class ExamCoursework(BaseModel):
    __tablename__ = 'exam_coursework'

    student_uid: str = Column(Integer, primary_key=True)
    program_course_id: int = Column(Integer, ForeignKey("program_courses.id"), nullable=False)
    exam_category_id: int = Column(Integer, ForeignKey("exam_categories.id"), nullable=False)
    assessment_number: int = Column(Integer, nullable=False)
    score: float = Column(Float, nullable=False)
    weight: float = Column(Float, nullable=False)
    overall_marks: float = Column(Float, nullable=False)

