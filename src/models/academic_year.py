from sqlalchemy import Column, Integer, String, DateTime

from src.models import BaseModel


class AcademicYear(BaseModel):
    __tablename__ = "academic_years"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, unique=False)
    status: int = Column(Integer, nullable=False, unique=False)
    start_date: DateTime = Column(DateTime, nullable=True, unique=False)
    end_date: DateTime = Column(DateTime, nullable=True, unique=False)
