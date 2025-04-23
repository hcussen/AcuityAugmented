from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List
from sqlalchemy import and_

import traceback

from app.config import settings
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

@router.post("/appointment")
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
        # now = datetime(2025, 4, 19, 12, 25, 27)  # Using provided timestamp
        now = datetime.now() 
        today_start = datetime(now.year, now.month, now.day)
        today_end = today_start + timedelta(days=1)
        today_day_of_week = now.weekday()
        # today_day_of_week = 1 # lock at tuesday for testing

        # Get all appointments for today
        today_appointments = db.query(Appointment).filter(
            and_(
                Appointment.start_time >= today_start,
                Appointment.start_time < today_end
            )
        ).order_by(Appointment.start_time).all()

        # Group appointments by hour
        hourly_diffs: Dict[str, Dict[str, List[dict]]] = {}
        center_open, center_close = settings.hours_open[today_day_of_week]
        center_open = datetime.strptime(center_open, '%H:%M')
        center_close = datetime.strptime(center_close, '%H:%M')
        hours_open = int((center_close - center_open).total_seconds() // 3600)  # Convert seconds to hours

        for i in range(hours_open):
            hourly_diffs[datetime.strftime(center_open + timedelta(hours=i), '%H:%M')] = {
                "hour": datetime.strftime(center_open + timedelta(hours=i), '%H:%M'),
                "added": [],
                "deleted": []
            }
        
        for appt in today_appointments:
            hour = appt.start_time.strftime('%H:%M')
            if hour not in hourly_diffs.keys():
                print(f'skipping {appt.id} at {hour}')
                continue
            if appt.is_deleted:
                hourly_diffs[hour]["deleted"].append({
                    "id": appt.id,
                    "first_name": appt.first_name,
                    "last_name": appt.last_name,
                    })
            else:   
                hourly_diffs[hour]["added"].append({
                    "id": appt.id,
                    "first_name": appt.first_name,
                    "last_name": appt.last_name,
                })

        return list(hourly_diffs.values())

    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
