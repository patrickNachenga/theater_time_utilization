from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class Program(BaseModel):
    __tablename__ = "programs"
    id: int = Column(Integer, primary_key=True, index=True)
    code: str = Column(String, nullable=False, unique=True)
    tcu_code: str = Column(String, nullable=True, unique=False)
    nacte_code: str = Column(String, nullable=True, unique=False)
    reg_code: str = Column(String, nullable=False)
    name: str = Column(String, nullable=False)
    short_name: str = Column(String, nullable=False, unique=False)
    program_category_id: int = Column(Integer, nullable=True, index=True)
    department_id: int = Column(Integer, nullable=True, index=True)
    campus_id: int = Column(String, nullable=True)
    duration: int = Column(Integer, nullable=False)






