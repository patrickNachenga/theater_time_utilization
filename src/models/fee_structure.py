from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from src.models import BaseModel


class FeeStructure(BaseModel):
    __tablename__ = "fee_structure"
    name: str = Column(String)
    amount: float = Column(Integer)
    currency: str = Column(String)
    min_amount: float = Column(Float)
    study_year: int = Column(Integer)
    program_id: int = Column(Integer, ForeignKey('programs.id'), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationship
    program = relationship("Program", lazy="subquery", back_populates="fee_structures")

    # table arguments for Unique together constraint with condition
    __table_args__ = (

        Index(
            'ix_unique_primary_content',  # Index name
            'name',
            'study_year',
            'program_id',  # Columns which are part of the index
            unique=True,
            postgresql_where=(Column('deleted_at').is_(None)),  # The condition
        ),
    )
