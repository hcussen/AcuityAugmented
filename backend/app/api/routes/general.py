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

@router.post("/mock_webhook")
def mock_webhook(
    action: str = Form(...),
    id: str = Form(...),
    calendarID: Optional[str] = Form(None),
    appointmentTypeID: Optional[str] = Form(None),
    db: Session = Depends(get_db)):
    try:
        # Check if appointment exists
        existing_appt = db.query(Appointment).filter_by(id=id).first()
        
        print(existing_appt)
        # Fetch appointment details from Acuity API
        try:
            appt_details: AcuityAppointment = acuity_client.get_appointment('1451596598')
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch appointment details: {str(e)}")
        
        # TODO: Process appointment details as needed
        print(appt_details)
        
        if existing_appt:
            pass
            # if changed to a different time today:
            #     update appointment start time
            # else if changed to not today:
            #     mark as soft-deleted in database
            # else if changed to canceled:
            #     mark as soft-deleted in database
            if appt_details.canceled:
                db.
                pass
            # else:
            #     // update other changed properties as needed
        else:
            pass
        #     if changed to scheduled for today:
        #     add to database
        # else if changed to rescheduled for today:
        #     add to database
        # else if changed to canceled and original time was today:
        #     // decision point: either ignore or add with canceled status
        # else:
        #     // don't add to database (not relevant for today)
        return {"status": "success", "message": f"Processed {action} for appointment {id}", "details": appt_details}
            
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}