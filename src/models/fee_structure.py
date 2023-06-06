from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from src.models import Program

class FeeStructure(BaseModel):
    __tablename__ = "fee_structure"
    uid: str = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    amount: float = Column(Integer)
    currency: str = Column(String)
    min_amount: float = Column(Float)

    #Relationship
    program: Program = relationship("Program", lazy="subquery", back_populates="fee_structure")



