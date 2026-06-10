import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)


from .academic_year_semester import AcademicYearSemester
from .academic_year import AcademicYear

# theatre models
from .procedure_delay_category import ProcedureDelayCategory
from .procedure_delay_cause import ProcedureDelayCause
from .procedure import Procedure
from .theatre_role import TheatreRole
from .theatre_member import TheatreMember
from .theatre_member_role import TheatreMemberRole
from .region import Region
from .internal_source import InternalSource
from .external_source import ExternalSource
from .theatre_unit import TheatreUnit
from .death_reason import DeathReason
from .theatre_time_record import TheatreTimeRecord
from .theatre_record_team_member import TheatreRecordTeamMember
from .theatre_record_delay import TheatreRecordDelay

