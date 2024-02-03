from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class StudentProgramChange(BaseModel):
    """
    In every start academic year a student  are able to change program if all minimum requirement pass
    """
    __tablename__ = "student_program_changes"
    student_uid: str = Column(String, nullable=False)
    approve_status: str = Column(String, nullable=False)
    current_registration_number: str = Column(String, nullable=False)
    approve_remark: str = Column(String, nullable=True)
    reason: str = Column(String, nullable=False)
    new_registration_number: str = Column(String, nullable=True)
    approved_by: str = Column(String, nullable=True)

    # ___________________________Foreign Keys ____________________________#
    academic_year_id: int = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_year = relationship('AcademicYear', lazy='subquery')

    current_program_id: int = Column(Integer, ForeignKey("programs.id"), nullable=False)
    current_program = relationship('Program', lazy='subquery', foreign_keys=[current_program_id])

    new_program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    new_program = relationship('Program', lazy='subquery', foreign_keys=[new_program_id])
