import strawberry
from typing import Optional


@strawberry.input
class TheatreTimeSettingInput:
    uid: Optional[str] = None
    start_cutting_time: str = ""  # "HH:MM" — time procedures begin every day
    room_preparation_minutes: int = 0
    patient_induction_minutes: int = 0


@strawberry.type
class TheatreTimeSettingNode:
    uid: str
    start_cutting_time: str
    room_preparation_minutes: int
    patient_induction_minutes: int
