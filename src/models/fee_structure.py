from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class FeeStructure(BaseModel):
    __tablename__ = "fee_structure"
    uid: str = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    amount: float = Column(Integer)
    currency: str = Column(String)
    min_amount: float = Column(Float)
    program_id: int = Column(Integer, ForeignKey('program.id'), nullable=False)

    #Relationship
    program = relationship("Program", lazy="subquery", back_populates="fee_structure")


