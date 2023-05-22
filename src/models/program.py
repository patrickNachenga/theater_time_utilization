from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class Program(BaseModel):
    __tablename__ = "program"
    id: int = Column(Integer, primary_key=True, index=True)
    program_number: int = Column(Integer, nullable=False, unique=True)
    code: int = Column(Integer, nullable=False, unique=False)
    name: str = Column(String, nullable=False, unique=True)
    short_name: str = Column(String, nullable=False, unique=False)
    tcu_code: str = Column(String, nullable=True, unique=False)
    duration: int = Column(Integer, nullable=False)
    qualification: int = Column(Integer, nullable=True, unique=False)
    max_student: int = Column(Integer, nullable=False)
    action: int = Column(Integer, nullable=True, index=True)
    # list of keys/relational attribute
    created_by: int = Column(Integer, nullable=True, index=True)
    program_type_id: int = Column(Integer, nullable=True, index=True)
    specialization_area_id: int = Column(Integer, nullable=True, index=True)
    institute_unit_id: int = Column(String, nullable=True, unique=True)


