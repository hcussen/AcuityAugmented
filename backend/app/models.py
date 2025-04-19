from typing import List, Optional
from sqlalchemy import String, DateTime, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[str] = mapped_column(DateTime)
    deleted_at: Mapped[str] = mapped_column(DateTime)
    is_deleted: Mapped[bool] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"Appt #{self.id}: {self.name} created_at: {self.created_at} deleted: {self.is_deleted} at {self.deleted_at}"
