from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseModel


class ExternalSource(BaseModel):
    __tablename__ = "external_sources"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)
    region_uid = Column(UUID(as_uuid=True), ForeignKey('regions.uid'), nullable=True)

