from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseModel


class TheatreRecordDelay(BaseModel):
    __tablename__ = "theatre_record_delays"
    record_uid = Column(UUID(as_uuid=True), ForeignKey('theatre_time_records.uid'), nullable=False)
    procedure_delay_category_uid = Column(UUID(as_uuid=True), ForeignKey('procedure_delay_categories.uid'), nullable=True)
    delay_cause_uid = Column(UUID(as_uuid=True), ForeignKey('procedure_delay_causes.uid'), nullable=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=True)

