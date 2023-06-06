from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship


class FeeStructure(BaseModel):
    __tablename__ = "fee_structure"
    name: str = Column(String)
    amount: float = Column(Integer)
    currency: str = Column(String)
    min_amount: float = Column(Float)
    program_id: int = Column(Integer)



