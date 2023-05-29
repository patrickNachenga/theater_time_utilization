from sqlalchemy import Column, String, Integer

from src.models import BaseModel


class Staff(BaseModel):
    __tablename__ = "staffs"
    id: int = Column(Integer, primary_key=True, index=True)
    pf_number: str = Column(String, nullable=False, unique=False)
