from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from src.models import BaseModel


class ProcedureDelayCause(BaseModel):
    __tablename__ = "procedure_delay_causes"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)
    description: str = Column(Text, nullable=True)
    procedure_delay_category_uid = Column(ForeignKey('procedure_delay_categories.uid'), nullable=False)

