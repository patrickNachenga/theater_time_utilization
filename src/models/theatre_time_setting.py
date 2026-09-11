from sqlalchemy import Column, Integer, Time

from src.models import BaseModel


class TheatreTimeSetting(BaseModel):
    """
    Global timing configuration used to auto-derive whether the first
    case of the day started late (see TheatreTimeRecordService._compute_had_delay).
    """
    __tablename__ = "theatre_time_settings"

    start_cutting_time = Column(Time, nullable=False)
    room_preparation_minutes = Column(Integer, nullable=False, default=0)
    patient_induction_minutes = Column(Integer, nullable=False, default=0)
