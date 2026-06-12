from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProcedureDelayCategory(BaseModel):
    __tablename__ = "procedure_delay_categories"
    name: str = Column(String(255), nullable=False)
    code = Column(String(50), unique=True)
    causes = relationship(
        "ProcedureDelayCause",
        back_populates="category"
    )

