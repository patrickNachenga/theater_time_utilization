from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel
from src.models.fee_structure import FeeStructure


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
    # ---------------Mapped Columns ---------------------
    program_category_id: int = Column(Integer, ForeignKey("program_categories.id"), nullable=False)
    program_category = relationship('ProgramCategory', lazy='subquery', back_populates="programs")

    #Relationship to the Fee Structure Model
    fee_structure: FeeStructure = relationship("FeeStructure", lazy='subquery', back_populates="program")

    department_uid: str = Column(String, nullable=True)

    campus_uid: str = Column(String, nullable=True)

    # ---------------Referenced Columns ---------------------
    program_semesters = relationship('ProgramSemester', lazy='subquery', back_populates="program")
