from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ExternalSource(BaseModel):
    __tablename__ = "external_sources"
    name: str = Column(String(255), nullable=False)
    code: str = Column(String(50), nullable=True)
    region_id = Column(ForeignKey("regions.id"), nullable=False, index=True)

    #RELATIONSHIP
    region = relationship("Region")


