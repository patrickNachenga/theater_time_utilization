from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class Program(BaseModel):
    __tablename__ = "programs"
    id: int = Column(Integer, primary_key=True, index=True)
    code: str = Column(String, nullable=False, unique=True)
    tcu_code: str = Column(String, nullable=True, unique=False)
    nacte_code: str = Column(String, nullable=True, unique=False)
    registration_code: str = Column(String, nullable=False)
    name: str = Column(String, nullable=False)
    short_name: str = Column(String, nullable=False, unique=False)
    duration: int = Column(Integer, nullable=False)
    # ---------------Mapped Columns ---------------------
    program_category_id: int = Column(Integer, ForeignKey("program_categories.id"), nullable=True, index=True)
    program_category = relationship('ProgramCategory', lazy='subquery', back_populates="programs")

    department_uid: str = Column(String, nullable=True, index=True)

    campus_id: int = Column(String, nullable=True)

    # ---------------Referenced Columns ---------------------
    program_semesters = relationship('ProgramSemester', lazy='subquery', back_populates="program")







