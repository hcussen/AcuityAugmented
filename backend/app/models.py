import uuid
import enum
from datetime import datetime
from typing import List 
from sqlalchemy import String, DateTime, Integer, Boolean, Uuid, func, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import  ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy_serializer import SerializerMixin

class Base(DeclarativeBase, SerializerMixin):
    pass

class Snapshot(Base):
    __tablename__ = 'snapshots'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    dump: Mapped[dict] = mapped_column(JSON)

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    acuity_id: Mapped[int] = mapped_column(Integer) #fk to Acuity ID
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))

    start_time: Mapped[datetime] = mapped_column(DateTime)
    duration: Mapped[int] = mapped_column(Integer, server_default="60") # in minutes

    acuity_created_at: Mapped[datetime] = mapped_column(DateTime)
    acuity_deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_canceled: Mapped[bool] = mapped_column(Boolean, nullable=True)
    
    # server metadata
    created_at_here: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_modified_here: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    events: Mapped[List["Event"]] = relationship(
        back_populates='appointment', 
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Appt #{self.id}: {self.first_name} {self.last_name} is_canceled: {self.is_canceled} acuity: {self.acuity_created_at}"

class EventAction(enum.Enum):
    schedule = 0
    reschedule_incoming = 1
    reschedule_same_day = 2
    reschedule_outgoing = 3
    cancel = 4

class Event(Base):
    __tablename__ = "events"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    action: Mapped[EventAction] = mapped_column(Enum(EventAction))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    old_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    new_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)


    appointment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, 
        ForeignKey("appointments.id", 
        ondelete="CASCADE")
    )
    appointment: Mapped["Appointment"] = relationship(back_populates='events')

    serialize_rules = ('-appointment',)
    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'action': self.action,
    #         'created_at': self.created_at,
    #         'old_time': self.old_time,
    #         'new_time': self.new_time,
    #         ''
    #     }
    # def __repr__():
    #     pass


    