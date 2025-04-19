from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
import requests

from app.core.acuityClient import acuity_client

from app.database import get_db
from app.models import Appointment

router = APIRouter(
    prefix="",
    tags=["general"],
)
# Request model for appointment creation
class AppointmentCreate(BaseModel):
    name: str
    start_time: datetime
    duration: int
    created_at: datetime

@router.post("/appointments")
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        db_appointment = Appointment(
            name=appointment.name,
            start_time=appointment.start_time,
            duration=appointment.duration,
            created_at=appointment.created_at,
        )
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

