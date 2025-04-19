from typing import List, Optional
from sqlalchemy import ForeignKey, String, Datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[str] = mapped_column(Datetime)
    deleted_at: Mapped[str] = mapped_column(Datetime)
    is_deleted: Mapped[bool] = mapped_column(int)

    def __repr__(self) -> str:
        return f"Appt #{self.id}: {self.name} created_at: {self.created_at} deleted: {self.is_deleted} at {self.deleted_at}"
