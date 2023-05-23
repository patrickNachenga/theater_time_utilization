from sqlalchemy import Column, Integer, String, Float

from src.models import BaseModel


class ProgramSemester(BaseModel):
    __tablename__ = "program_sem_unit"
    id: int = Column(Integer, primary_key=True, index=True, unique=False)
    program_code: str = Column(String, nullable=False)
    ac_year: int = Column(Integer, nullable=False)
    study_year: int = Column(Integer, nullable=False)
    semester: int = Column(Integer, nullable=False)
    core_cwt: float = Column(Float(4), nullable=False)
    opt_cwt: float = Column(Float(4), nullable=False)
    created_by: str = Column(Integer, nullable=True, index=True)
