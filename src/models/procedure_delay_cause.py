from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProcedureDelayCause(BaseModel):
    __tablename__ = "procedure_delay_causes"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)
    description: str = Column(Text, nullable=True)
    procedure_delay_category_id = Column(ForeignKey('procedure_delay_categories.id'), nullable=False, index=True)
    procedure_delay_category = relationship("ProcedureDelayCategory")

