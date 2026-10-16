from enum import Enum

from sqlalchemy import Column, String, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.models import BaseModel


class TheatreRoomStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class TheatreRoom(BaseModel):
    """
    A physical operating room inside a TheatreUnit. Procedures are performed
    in a specific room, not just the unit, so turnaround/delay analysis can
    be scoped per room (see TheatreProcedureRecord.theatre_room_id).
    """
    __tablename__ = "theatre_rooms"
    __table_args__ = (UniqueConstraint("theatre_unit_id", "name", name="uq_theatre_room_unit_name"),)

    theatre_unit_id = Column(ForeignKey("theatre_units.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    category = Column(String(255), nullable=True)
    capacity = Column(Integer, nullable=True)
    equipment_notes = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TheatreRoomStatus), nullable=False, default=TheatreRoomStatus.OPEN, index=True)

    theatre_unit = relationship("TheatreUnit")
