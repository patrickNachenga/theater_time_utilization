from sqlalchemy import Column, String, Date, Time, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseModel


class TheatreTimeRecord(BaseModel):
    __tablename__ = "theatre_time_records"
    patient_mrn = Column(String(100), nullable=True)
    patient_dob = Column(Date, nullable=True)
    patient_sex = Column(String(10), nullable=True)
    patient_region_uid = Column(UUID(as_uuid=True), ForeignKey('regions.uid'), nullable=True)
    patient_type = Column(String(20), nullable=True)
    patient_source_type = Column(String(20), nullable=True)
    internal_source_uid = Column(UUID(as_uuid=True), ForeignKey('internal_sources.uid'), nullable=True)
    external_source_uid = Column(UUID(as_uuid=True), ForeignKey('external_sources.uid'), nullable=True)
    theatre_unit_uid = Column(UUID(as_uuid=True), ForeignKey('theatre_units.uid'), nullable=True)
    procedure_uid = Column(UUID(as_uuid=True), ForeignKey('procedures.uid'), nullable=True)
    procedure_date = Column(Date, nullable=True)
    procedure_start_time = Column(Time, nullable=True)
    procedure_end_time = Column(Time, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    estimated_procedure_minutes = Column(Integer, nullable=True)
    time_variance_minutes = Column(Integer, nullable=True)
    surgery_met_time_between_cases = Column(String(10), nullable=True)
    was_there_delay = Column(String(10), nullable=True)
    surgery_beyond_theatre_time = Column(String(10), nullable=True)
    delay_cause_between_cases = Column(Text, nullable=True)
    patient_outcome = Column(String(20), nullable=True)
    discharge_destination = Column(String(20), nullable=True)
    discharge_internal_source_uid = Column(UUID(as_uuid=True), ForeignKey('internal_sources.uid'), nullable=True)
    death_reason_uid = Column(UUID(as_uuid=True), ForeignKey('death_reasons.uid'), nullable=True)
    death_description = Column(Text, nullable=True)
    surgeon_name = Column(Text, nullable=True)
    anesthetist_name = Column(Text, nullable=True)
    scrub_nurse_name = Column(Text, nullable=True)
    runner_nurse_name = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)

