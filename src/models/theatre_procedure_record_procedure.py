from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.models import BaseModel


class TheatreProcedureRecordProcedure(BaseModel):
    """
    One procedure performed within a case. A case (TheatreProcedureRecord)
    may list several of these - the case still has a single shared
    start/end time, and estimated_minutes here is a snapshot of the
    procedure's estimate at the time the case was saved (so later edits to
    the Procedure lookup don't silently rewrite historical cases).
    """
    __tablename__ = "theatre_procedure_record_procedures"

    record_id = Column(ForeignKey("theatre_procedure_records.id"), nullable=False, index=True)
    procedure_id = Column(ForeignKey("procedures.id"), nullable=False, index=True)
    estimated_minutes = Column(Integer, nullable=True)
    rank = Column(Integer, nullable=True)

    record = relationship("TheatreProcedureRecord", back_populates="procedures")
    procedure = relationship("Procedure")
