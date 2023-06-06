from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from src.models import BaseModel


class FeeStructure(BaseModel):
    __tablename__ = "fee_structures"
    name: str = Column(String, nullable=False)
    amount: float = Column(Float(4), nullable=False)
    currency: str = Column(String, nullable=False)
    min_amount: float = Column(Float(4), nullable=False)
    # ---------------Mapped Columns ---------------------
    program_id: int = Column(Integer, ForeignKey("programs.id"), nullable=False)
    program = relationship("Program", lazy='subquery', back_populates="fee_structures")






