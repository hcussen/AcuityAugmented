from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
from sqlalchemy import and_

from app.types import AcuityAppointment
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
    id: int 
    first_name: str
    last_name: str
    start_time: datetime
    duration: int
    acuity_created_at: datetime

@router.post("/appointments")
def create_appointment(appt: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        db_appointment = Appointment(
            id=appt.id,
            first_name=appt.first_name,
            last_name=appt.last_name,
            start_time=appt.start_time,
            duration=appt.duration,
            acuity_created_at=appt.acuity_created_at
        )
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/schedule/diff")
def get_schedule_diff(db: Session = Depends(get_db)):
    try:
        # Get current date boundaries
        now = datetime(2025, 4, 19, 12, 25, 27)  # Using provided timestamp
        today_start = datetime(now.year, now.month, now.day)
        today_end = today_start + timedelta(days=1)

        # Get all appointments for today
        today_appointments = db.query(Appointment).filter(
            and_(
                Appointment.start_time >= today_start,
                Appointment.start_time < today_end
            )
        ).all()

        # Group appointments by hour
        hourly_diffs: Dict[int, Dict[str, List[dict]]] = {}
        for hour in range(24):
            hour_start = today_start + timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)
            
            # Filter appointments for this hour
            hour_appointments = [
                {
                    "id": appt.id,
                    "first_name": appt.first_name,
                    "last_name": appt.last_name,
                    "start_time": appt.start_time.isoformat(),
                    "duration": appt.duration
                }
                for appt in today_appointments
                if hour_start <= appt.start_time < hour_end
            ]

            # For now, we'll consider all appointments as "added"
            # In a real implementation, you would compare with a previous state
            # stored in the database or cache to determine added/deleted
            hourly_diffs[hour] = {
                "added": hour_appointments,
                "deleted": []
            }

        return hourly_diffs

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
