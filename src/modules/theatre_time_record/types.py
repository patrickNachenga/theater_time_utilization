import strawberry
from typing import List, Optional


@strawberry.input
class TheatreTimeRecordInput:
    uid: Optional[str] = None
    patient_mrn: Optional[str] = None
    patient_dob: Optional[str] = None
    patient_sex: Optional[str] = None
    patient_region_uid: Optional[str] = None
    patient_type: Optional[str] = None
    patient_source_type: Optional[str] = None
    internal_source_uid: Optional[str] = None
    external_source_uid: Optional[str] = None
    theatre_unit_uid: Optional[str] = None
    procedure_uid: Optional[str] = None
    procedure_date: Optional[str] = None


@strawberry.type
class TheatreTimeRecordNode:
    uid: str
    patient_mrn: Optional[str]
    procedure_date: Optional[str]


@strawberry.type
class TheatreTimeRecordListNode:
    items: List[TheatreTimeRecordNode]
    total_count: int
