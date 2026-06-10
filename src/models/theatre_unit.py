from sqlalchemy import Column, String
from src.models import BaseModel


class TheatreUnit(BaseModel):
    __tablename__ = "theatre_units"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)
    location: str = Column(String(255), nullable=True)

