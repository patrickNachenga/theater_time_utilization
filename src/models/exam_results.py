from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.models import BaseModel

class ExamResults(BaseModel):
    __tablename__ = "exam_results"
    id:                 int = Column(Integer, primary_key=True, index=True)
    program_course_id:    int = Column(Integer, nullable=False, unique=False)
    exam_cat_id:          int = Column(Integer, nullable=False, unique=False)
    student_id:          int = Column(Integer, nullable=False, unique=False)
    assess_no:           int = Column(Integer, nullable=False, unique=False)
    score:              float = Column(Integer, nullable=False, unique=False)
    out_of:             float = Column(Integer, nullable=False, unique=False)
    weight:             int = Column(Integer, nullable=False, unique=False)
    status:             int = Column(Integer, nullable=False, unique=False)
    publish:            int = Column(Integer, nullable=False, unique=False)
