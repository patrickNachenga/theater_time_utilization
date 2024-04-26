from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship

from src.models import BaseModel


class UploadResultDeadline(BaseModel):
    __tablename__ = "upload_result_deadline"
    department_uid: str = Column(String, nullable=False, unique=False)
    end_date: Date = Column(Date, nullable=True)
    academic_year_semester_id: int = Column(Integer, ForeignKey("academic_year_semesters.id"), nullable=False)
    academic_year_semester = relationship('AcademicYearSemester', lazy='subquery')
