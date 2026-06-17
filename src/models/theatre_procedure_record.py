from enum import Enum

from sqlalchemy import Column, String, Date, Time, Integer, Text, ForeignKey, Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models import BaseModel


class PatientOutcome(str, Enum):
    DEATH = "DEATH"
    DISCHARGED = "DISCHARGED"


class PatientType(str, Enum):
    ELECTIVE = "ELECTIVE"
    EMERGENCY = "EMERGENCY"


class SourceType(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


class YesNo(str, Enum):
    YES = "YES"
    NO = "NO"


class TeamRole(str, Enum):
    SURGEON = "SURGEON"
    ANESTHETIST = "ANESTHETIST"
    SCRUB_NURSE = "SCRUB_NURSE"
    RUNNER_NURSE = "RUNNER_NURSE"


class DischargeDirection(str, Enum):
    INTERNAL = "INTERNAL"
    HOME = "HOME"


class TheatreProcedureRecord(BaseModel):
    __tablename__ = "theatre_procedure_records"
    # Patient Demographics
    patient_mrn = Column(String(100), nullable=True)
    patient_dob = Column(Date, nullable=True)
    patient_sex = Column(String(10), nullable=True)
    patient_region_id = Column(ForeignKey("regions.id"), index=True)
    patient_type = Column(SQLEnum(PatientType), nullable=False, index=True)
    # Patient source.
    patient_source_type = Column(SQLEnum(SourceType), nullable=False)
    internal_source_id = Column(ForeignKey("internal_sources.id"), nullable=True)
    external_source_id = Column(ForeignKey("external_sources.id"), nullable=True)
    # Theatre and Procedure
    theatre_unit_id = Column(ForeignKey("theatre_units.id"), nullable=False, index=True)
    procedure_id = Column(ForeignKey("procedures.id"), nullable=False, index=True)
    procedure_date = Column(Date, nullable=False, index=True)
    procedure_start_time = Column(Time, nullable=False)
    procedure_end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=True)
    variance_minutes = Column(Integer, nullable=True)
    met_turnaround_target = Column(Boolean, nullable=True)
    had_delay = Column(Boolean, nullable=False, default=False, index=True)
    delay_reason = Column(Text, nullable=True)
    surgery_beyond_theatre_time = Column(Boolean, nullable=True)
    surgery_met_time_between_cases = Column(Boolean, nullable=True)

    # OUTCOME of Procedure
    outcome = Column(SQLEnum(PatientOutcome), nullable=False, index=True)
    discharge_direction = Column(SQLEnum(DischargeDirection), nullable=True, index=True)
    discharge_destination_id = Column(ForeignKey("internal_sources.id"), nullable=True)
    death_reason_id = Column(ForeignKey("death_reasons.id"), nullable=True)
    death_description = Column(Text, nullable=True)

    # ==========================
    # RELATIONSHIPS
    # ==========================
    patient_region = relationship("Region")
    theatre_unit = relationship("TheatreUnit")
    procedure = relationship("Procedure")
    internal_source = relationship("InternalSource", foreign_keys=[internal_source_id])
    external_source = relationship("ExternalSource", foreign_keys=[external_source_id])
    discharge_destination = relationship("InternalSource", foreign_keys=[discharge_destination_id])
    death_reason = relationship("DeathReason")
    delay_courses = relationship("TheatreRecordDelay", back_populates="record", cascade="all, delete-orphan")
    team_members = relationship("TheatreRecordTeamMember", back_populates="team_member",
                                cascade="all, delete-orphan")
