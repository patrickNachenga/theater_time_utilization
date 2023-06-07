from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel

class FeeStructure(BaseModel):
    __tablename__ = "fee_structure"
    name: str = Column(String)
    amount: float = Column(Integer)
    currency: str = Column(String)
    min_amount: float = Column(Float)
    study_year: int = Column(Integer)
    program_id: int = Column(Integer, ForeignKey('programs.id'), nullable=False)

    #Relationship
    program = relationship("Program", lazy="subquery", back_populates="fee_structures")






