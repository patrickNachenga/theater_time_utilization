from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class Programme(BaseModel):
    __tablename__ = "programme"
    id: int = Column(Integer, primary_key=True, index=True)
    programme_number: int = Column(int, nullable=False, unique=True)
    code: int = Column(Integer, nullable=False, unique=False)
    name: str = Column(String, nullable=False, unique=True)
    short_name: str = Column(String, nullable=False, unique=False)
    tcu_code: str = Column(String, nullable=True, unique=False)
    duration: int = Column(int, nullable=False)
    qualification: int = Column(String, nullable=True, unique=False)
    max_student: int = Column(Integer, nullable=False)
    action: int = Column(String, nullable=True, index=True)
    # list of keys/relational attribute
    created_by: int = Column(int, nullable=True, index=True)
    programme_type_id: int = Column(int, nullable=True, index=True)
    specialization_area_id: int = Column(int, nullable=True, index=True)
    institute_unit_id: str = Column(String, nullable=True, unique=True)


