from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class SeminarType(BaseModel):
    __tablename__ = "seminar_types"
    name: str = Column(String, nullable=False, unique=False)
    description: str = Column(String, nullable=False, unique=False)
    rank: int = Column(Integer, nullable=False, unique=False)

# ---------------- Relationships -----------------------------#

    student_seminar = relationship("StudentSeminar", lazy="noload",
                                                back_populates="seminar_types")