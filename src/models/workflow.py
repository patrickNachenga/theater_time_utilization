import json
import uuid

from sqlalchemy import Column, String, PickleType, Integer, ForeignKey, DateTime, desc
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import Mutable
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


class JsonEncodedList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, JsonEncodedList):
            if isinstance(value, list):
                return JsonEncodedList(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def append(self, value):
        list.append(self, value)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()


class TransitionApprovalMeta(BaseModel):
    __tablename__ = 'transition_approval_meta'

    workflow_id = Column(Integer, ForeignKey('workflows.id'))
    transition_meta_id = Column(Integer, ForeignKey('transition_meta.id'))

    # Relationships
    workflow = relationship('Workflow', backref='transition_approval_metas')
    transition_meta = relationship('TransitionMeta', backref='transition_approval_metas')
    permission_codes = Column(JsonEncodedList.as_mutable(PickleType(pickler=json)))
    group_codes = Column(JsonEncodedList.as_mutable(PickleType(pickler=json)))


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
