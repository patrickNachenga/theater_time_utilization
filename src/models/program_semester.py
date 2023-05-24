from sqlalchemy import Column, Integer, String, Float

from src.models import BaseModel


class ProgramSemester(BaseModel):
    __tablename__ = "program_semester"
    id: int = Column(Integer, primary_key=True, index=True, unique=False)
    program_id: str = Column(String, nullable=False)
    academic_year_id: str = Column(String, nullable=False)
    study_year: int = Column(Integer, nullable=False)
    semester: int = Column(Integer, nullable=False)
    core_credits: float = Column(Float(4), nullable=False)
    elective_credits: float = Column(Float(4), nullable=False)
    created_by: str = Column(String, nullable=True, index=True)
