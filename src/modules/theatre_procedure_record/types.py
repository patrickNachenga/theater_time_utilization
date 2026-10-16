from dataclasses import dataclass

import strawberry
from typing import List, Optional
from enum import Enum

from ..region.types import RegionNode
from ..internal_source.types import InternalSourceNode
from ..external_source.types import ExternalSourceNode
from ..theatre_unit.types import TheatreUnitNode
from ..theatre_room.types import TheatreRoomNode
from ..procedure.types import ProcedureNode
from ..death_reason.types import DeathReasonNode
from ..theatre_record_team_member.types import TheatreRecordTeamMemberInput, TheatreRecordTeamMemberNode
from ..theatre_record_delay.types import TheatreRecordDelayInput, TheatreRecordDelayNode


@strawberry.input
class TheatreProcedureRecordProcedureInput:
    procedure_uid: str
    estimated_minutes: Optional[int] = None


@strawberry.type
class TheatreProcedureRecordProcedureNode:
    uid: str
    procedure: Optional[ProcedureNode]
    estimated_minutes: Optional[int]
    rank: Optional[int]


@strawberry.type
class PreviousCaseGapNode:
    found: bool
    previous_end_time: Optional[str]
    previous_procedure_names: Optional[str]
    gap_minutes: Optional[int]
    required_minutes: Optional[int]
    suggested_had_delay: Optional[bool]


@strawberry.enum
class PatientOutcome(str, Enum):
    DEATH = "DEATH"
    DISCHARGED = "DISCHARGED"

@strawberry.enum
class PatientType(str, Enum):
    ELECTIVE = "ELECTIVE"
    EMERGENCY = "EMERGENCY"

@strawberry.enum
class SourceType(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"

@strawberry.enum
class DischargeDirection(str, Enum):
    INTERNAL = "INTERNAL"
    HOME = "HOME"


@strawberry.input
class TheatreProcedureRecordInput:
    uid: Optional[str] = None
    patient_mrn: Optional[str] = None
    patient_dob: Optional[str] = None
    patient_sex: Optional[str] = None
    patient_region_uid: Optional[str] = None
    patient_region_id: Optional[int] = None
    patient_type: Optional[PatientType] = None
    patient_source_type: Optional[SourceType] = None
    internal_source_uid: Optional[str] = None
    internal_source_id: Optional[int] = None
    external_source_uid: Optional[str] = None
    external_source_id: Optional[int] = None
    theatre_unit_uid: Optional[str] = None
    theatre_unit_id: Optional[int] = None
    theatre_room_uid: Optional[str] = None
    theatre_room_id: Optional[int] = None
    procedures: Optional[List[TheatreProcedureRecordProcedureInput]] = None
    procedure_date: Optional[str] = None
    patient_induction_start_time: Optional[str] = None
    procedure_start_time: Optional[str] = None
    procedure_end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    estimated_duration_minutes: Optional[int] = None
    variance_minutes: Optional[int] = None
    met_turnaround_target: Optional[bool] = None
    had_delay: Optional[bool] = None
    delay_reason: Optional[str] = ""
    surgery_beyond_theatre_time: Optional[bool] = None
    is_first_case_of_day: Optional[bool] = None
    surgery_met_time_between_cases: Optional[bool] = None
    surgery_exceeded_estimated_time: Optional[bool] = None
    surgery_exceeded_time_description: Optional[str] = None
    outcome: Optional[PatientOutcome] = None
    discharge_direction: Optional[DischargeDirection] = None
    discharge_destination_uid: Optional[str] = None
    discharge_destination_id: Optional[int] = None
    death_reason_uid: Optional[str] = None
    death_reason_id: Optional[int] = None
    death_description: Optional[str] = None
    team_members: Optional[List[TheatreRecordTeamMemberInput]] = None
    delay_courses: Optional[List[TheatreRecordDelayInput]] = None


@dataclass
class TheatreProcedureRecordDTO:
    uid: str
    patient_mrn: str
    patient_dob: str
    patient_sex: str
    patient_region_id: int
    patient_type: PatientType
    patient_source_type: SourceType
    internal_source_id: Optional[int]
    external_source_id: Optional[int]
    theatre_unit_id: int
    theatre_room_id: Optional[int]
    procedure_date: str
    patient_induction_start_time: Optional[str]
    procedure_start_time: str
    procedure_end_time: str
    duration_minutes: int
    estimated_duration_minutes: int
    variance_minutes: int
    met_turnaround_target: bool
    had_delay: bool
    delay_reason: Optional[str]
    surgery_beyond_theatre_time: Optional[bool]
    is_first_case_of_day: Optional[bool]
    surgery_met_time_between_cases: Optional[bool]
    surgery_exceeded_estimated_time: Optional[bool]
    surgery_exceeded_time_description: Optional[str]
    outcome: PatientOutcome
    discharge_direction: Optional[DischargeDirection]
    discharge_destination_id: Optional[int]
    death_reason_id: Optional[int]
    death_description: Optional[str]

@strawberry.type
class TheatreProcedureRecordNode:
    uid: str
    patient_mrn: Optional[str]
    patient_dob: Optional[str]
    patient_sex: Optional[str]
    patient_region: Optional[RegionNode]
    patient_type: Optional[PatientType]
    patient_source_type: Optional[SourceType]
    internal_source: Optional[InternalSourceNode]
    external_source: Optional[ExternalSourceNode]
    theatre_unit: Optional[TheatreUnitNode]
    theatre_room: Optional[TheatreRoomNode]
    procedure: Optional[ProcedureNode]
    procedures: Optional[List[TheatreProcedureRecordProcedureNode]]
    procedure_date: Optional[str]
    patient_induction_start_time: Optional[str]
    procedure_start_time: Optional[str]
    procedure_end_time: Optional[str]
    duration_minutes: Optional[int]
    estimated_duration_minutes: Optional[int]
    variance_minutes: Optional[int]
    met_turnaround_target: Optional[bool]
    had_delay: Optional[bool]
    delay_reason: Optional[str]
    surgery_beyond_theatre_time: Optional[bool]
    is_first_case_of_day: Optional[bool]
    surgery_met_time_between_cases: Optional[bool]
    surgery_exceeded_estimated_time: Optional[bool]
    surgery_exceeded_time_description: Optional[str]
    outcome: Optional[PatientOutcome]
    discharge_direction: Optional[DischargeDirection]
    discharge_destination: Optional[InternalSourceNode]
    death_reason: Optional[DeathReasonNode]
    death_description: Optional[str]
    team_members: Optional[List[TheatreRecordTeamMemberNode]]
    delay_courses: Optional[List[TheatreRecordDelayNode]]


@strawberry.type
class TheatreProcedureRecordSimpleNode:
    uid: str
    patient_mrn: Optional[str]
    patient_dob: Optional[str]
    patient_sex: Optional[str]
    patient_type: Optional[PatientType]
    procedure_date: Optional[str]
    procedure_start_time: Optional[str]
    procedure_end_time: Optional[str]
    duration_minutes: Optional[int]
    had_delay: Optional[bool]
    outcome: Optional[PatientOutcome]
    created_by: Optional[str]
    patient_region: Optional[RegionNode]
    procedure: Optional[ProcedureNode]
    procedures: Optional[List[TheatreProcedureRecordProcedureNode]]
    theatre_unit: Optional[TheatreUnitNode]
    theatre_room: Optional[TheatreRoomNode]


@strawberry.type
class TheatreTimeRecordListNode:
    items: List[TheatreProcedureRecordSimpleNode]
    total_count: int