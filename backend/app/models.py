from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True) #fk to Acuity ID
    first_name: Mapped[str] = mapped_column(String(30), server_default="'John'")
    last_name: Mapped[str] = mapped_column(String(30), server_default="'Doe'")
    start_time: Mapped[str] = mapped_column(DateTime)
    duration: Mapped[int] = mapped_column(Integer)
    acuity_created_at: Mapped[str] = mapped_column(DateTime)
    acuity_deleted_at: Mapped[str] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=True)
    
    created_at_here: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_modified_here: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Appt #{self.id}: {self.first_name} {self.last_name} is_deleted: {self.is_deleted} acuity: {self.acuity_created_at}"
