from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from src.models import BaseModel


class TheatreRecordDelay(BaseModel):
    __tablename__ = "theatre_record_delays"

    record_id = Column(ForeignKey("theatre_procedure_records.id"), nullable=False, index=True)
    category_id = Column(ForeignKey("procedure_delay_categories.id"), nullable=False)
    cause_id = Column(ForeignKey("procedure_delay_causes.id"), nullable=False)
    description = Column(Text)

    #  RELATIONSHIP
    record = relationship("TheatreProcedureRecord", back_populates="delay_courses")
    category = relationship("ProcedureDelayCategory")
    cause = relationship("ProcedureDelayCause")
