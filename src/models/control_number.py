from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ControlNumber(BaseModel):
    __tablename__ = "control_numbers"
    registration_number: str = Column(String)
    fee_name: str = Column(String)
    amount: float = Column(Float)
    control_number = Column(String)
    currency: str = Column(String)
    pay_type: str = Column(String)
    academic_year: str = Column(String)
    bill_id: str = Column(String)
