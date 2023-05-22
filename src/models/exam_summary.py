from sqlalchemy import Column, Integer, String, FLOAT

from src.models import BaseModel

class ExamSummary(BaseModel):
    __tablename__ = "exam_summary"
    id:                 int = Column(Integer, primary_key=True, index=True)
    program_course_id:    int = Column(Integer, nullable=False, unique=False)
    student_id:          int = Column(Integer, nullable=False, unique=False)
    marks:              float = Column(FLOAT(10), nullable=False, unique=False)
    gp:                 float = Column(FLOAT(10), nullable=False, unique=False)
    grade:              chr(5) = Column(String,nullable=False, unique=False)
    remarks:            chr(15) = Column(String,nullable=False, unique=False)
    status:             int = Column(Integer, nullable=False, unique=False)

