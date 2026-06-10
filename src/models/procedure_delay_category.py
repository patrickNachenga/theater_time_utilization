from sqlalchemy import Column, String, Text, DateTime
from src.models import BaseModel


class ProcedureDelayCategory(BaseModel):
    __tablename__ = "procedure_delay_categories"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)
    description: str = Column(Text, nullable=True)

