import json
import uuid

from sqlalchemy import Column, String, PickleType, Integer, ForeignKey, DateTime, desc, CheckConstraint, \
    UniqueConstraint, JSON, Boolean, event, and_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import Mutable, MutableList
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID

from src.models import BaseModel


class Workflow(BaseModel):
    __tablename__ = 'workflows'
    name = Column(String)
    description = Column(String)
    processes = relationship('Process', lazy='subquery', back_populates="workflow")
    transition_metas = relationship('TransitionMeta', lazy='subquery', back_populates="workflow")


class State(BaseModel):
    __tablename__ = 'states'

    label = Column(String)
    description = Column(String)
    process_flows = relationship('ProcessFlow', lazy='subquery', back_populates="state")


class TransitionMeta(BaseModel):
    __tablename__ = 'transition_meta'

    workflow_id = Column(Integer, ForeignKey('workflows.id'))
    source_state_id = Column(Integer, ForeignKey('states.id'))
    destination_state_id = Column(Integer, ForeignKey('states.id'))

    # Relationships
    workflow = relationship('Workflow', lazy='subquery', back_populates="transition_metas")
    source_state = relationship('State', foreign_keys=[source_state_id])
    destination_state = relationship('State', foreign_keys=[destination_state_id])

    permissions = Column(MutableList.as_mutable(PickleType), default=list)
    groups = Column(MutableList.as_mutable(PickleType), default=list)
    deleted_at = Column(DateTime, nullable=True)
    is_first: bool = Column(Boolean, default=False)
    is_last: bool = Column(Boolean, default=False)

    # Adding Check and Unique Constraints
    # __table_args__ = (
    #     CheckConstraint(source_state_id != destination_state_id, name='check_different_states'),
    #     UniqueConstraint('source_state_id', 'destination_state_id', name='uix_source_destination'),
    # )


# Event listener for new inserts or updates on is_first
@event.listens_for(TransitionMeta, 'before_insert')
@event.listens_for(TransitionMeta, 'before_update')
def unset_is_first(mapper, connection, target):
    if target.is_first and target.deleted_at is None:
        # Unset `is_first` attribute of all other instances with the same workflow_id
        connection.execute(
            TransitionMeta.__table__.update().where(
                and_(
                    TransitionMeta.workflow_id == target.workflow_id,
                    TransitionMeta.is_first == True,
                    TransitionMeta.deleted_at.is_(None)
                )
            ).values(is_first=False)
        )


# Event listener for new inserts or updates on is_last
@event.listens_for(TransitionMeta, 'before_insert')
@event.listens_for(TransitionMeta, 'before_update')
def unset_is_last(mapper, connection, target):
    if target.is_last and target.deleted_at is None:
        # Unset `is_last` attribute of all other instances with the same workflow_id
        connection.execute(
            TransitionMeta.__table__.update().where(
                and_(
                    TransitionMeta.workflow_id == target.workflow_id,
                    TransitionMeta.is_last == True,
                    TransitionMeta.deleted_at.is_(None)
                )
            ).values(is_last=False)
        )


class Process(BaseModel):
    __tablename__ = 'processes'
    description = Column(String(255), nullable=False)
    process_unique_uid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    workflow_id: int = Column(Integer, ForeignKey("workflows.id"))
    workflow: Mapped["Workflow"] = relationship('Workflow', lazy='subquery', back_populates="processes")
    process_flows = relationship('ProcessFlow', lazy='subquery', back_populates="process")
    completed_on = Column(DateTime, nullable=True)

    @hybrid_property
    def current_state(self):
        """
        Returns the instance of the ProcessFlow model that represents the
        current step this Process is in.
        """
        if self.process_flows:
            return self.process_flows.order_by(desc(ProcessFlow.created_at)).first()
        else:
            return None


class ProcessFlow(BaseModel):
    __tablename__ = 'process_flows'
    state_id = Column(ForeignKey('states.id'))
    process_id = Column(ForeignKey('processes.id'))
    state = relationship("State", lazy='subquery', back_populates="process_flows")
    process = relationship("Process", lazy='subquery', back_populates="process_flows")
    comment = Column(String(255), nullable=True)
