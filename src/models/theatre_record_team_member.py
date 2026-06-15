from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.models import BaseModel
from src.models.theatre_procedure_record import TeamRole


class TheatreRecordTeamMember(BaseModel):
    __tablename__ = "theatre_record_team_members"

    record_id = Column( ForeignKey("theatre_procedure_records.id"),nullable=False, index=True)
    theatre_member_id = Column( ForeignKey("theatre_members.id"),nullable=False,  index=True )
    role = Column( SQLEnum(TeamRole),nullable=False, index=True )
    rank =  Column(Integer, nullable=True, index=True)

    # RELATIONSHIPS
    record = relationship("TheatreProcedureRecord",  back_populates="team_members" )
    theatre_member = relationship(  "TheatreMember"  )