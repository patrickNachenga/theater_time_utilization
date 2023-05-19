from sqlalchemy import Column, Integer, String

from src.models import BaseModel

class ProgramCategory(BaseModel):
    __tablename__ = "program_category"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, unique=True)
    code: str = Column(String, nullable=True, unique=False)
