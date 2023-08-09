from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, joinedload

from src.db.session import session_scope
from src.models import BaseModel, Program


class StudentProgramChange(BaseModel):
    """
    In every start academic year a student  are able to change program if all minimum requirement pass
    """
    __tablename__ = "student_program_changes"
    student_uid: str = Column(String, nullable=False)
    approve_status: str = Column(String, nullable=False)
    approve_remark: str = Column(String, nullable=False)
    reason: str = Column(String, nullable=False)
    current_registration_number: str = Column(String, nullable=False)
    new_registration_number: str = Column(String, nullable=True)
    approved_by: str = Column(String, nullable=True)

    # ___________________________Foreign Keys ____________________________#
    academic_year_id: int = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    academic_year = relationship('AcademicYear', lazy='subquery', back_populates="student_program_changes")

    # current_program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    # current_program = relationship("Program", lazy='subquery', foreign_keys=[current_program_id], back_populates="current_program_student_program_changes", )
    #
    # new_program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    # new_program = relationship('Program', lazy='subquery', foreign_keys=[new_program_id], back_populates='new_program_student_program_changes')
    #
