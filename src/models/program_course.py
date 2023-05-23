from sqlalchemy import Column, Integer, String, Float

from src.models import BaseModel


class ProgramCourse(BaseModel):
    __tablename__ = "program_course"
    id: int = Column(Integer, primary_key=True, index=True, unique=False)
    sem_units_id: int = Column(Integer, nullable=True)
    course_code: str = Column(String, nullable=False)
    crelid: int = Column(Integer, nullable=False)
    cwt: int = Column(Integer, nullable=False)
    lhr: int = Column(Integer, nullable=False)
    shr: int = Column(Integer, nullable=False)
    phr: int = Column(Integer, nullable=True)
    ash: int = Column(Integer, nullable=True)
    ish: int = Column(Integer, nullable=True)
    created_by: int = Column(Integer, nullable=True, index=True)
    passmark: float = Column(Float(precision=4), nullable=True, index=True)
    action: str = Column(String[1], nullable=True, unique=True)




