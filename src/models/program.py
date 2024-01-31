from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class Program(BaseModel):
    __tablename__ = "programs"
    code: str = Column(String, nullable=False, unique=False)
    tcu_code: str = Column(String, nullable=True, unique=False)
    nacte_code: str = Column(String, nullable=True, unique=False)
    registration_code: str = Column(String, nullable=False)
    name: str = Column(String, nullable=False)
    short_name: str = Column(String, nullable=False, unique=False)
    duration: int = Column(Integer, nullable=False)
    moodle_id: str = Column(String, nullable=True)

    program_id = Column(Integer, index=True)
    # ---------------Mapped Columns ---------------------
    program_category_id: int = Column(Integer, ForeignKey("program_categories.id"), nullable=False)
    program_category = relationship('ProgramCategory', lazy='noload', back_populates="programs")

    department_uid: str = Column(String, nullable=True)

    campus_uid: str = Column(String, nullable=True)

    # ---------------Referenced Columns ---------------------
    program_semesters = relationship('ProgramSemester', lazy='noload', back_populates="program")
    program_capacities = relationship('ProgramCapacity', lazy='noload', back_populates="program")
    # Add the reverse relationship for current_program in Program
    # current_program_student_program_changes = relationship("StudentProgramChange", lazy='subquery',
    #                                                        back_populates="current_program")
    # new_program_student_program_changes = relationship("StudentProgramChange", lazy='subquery',
    #                                                    back_populates="new_program")
