from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests
from datetime import datetime 
from app.config import settings

import traceback

from app.core.acuityClient import acuity_client

from app.database import get_db
from app.models import Appointment, Event, EventAction
from app.core.apptActions import isToday, createNewAppointment, updateStartTime, markAsSoftDelete

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/appt-changed")
async def handle_appt_changed(
    action: str = Form(...),
    id: str = Form(...),
    calendarID: Optional[str] = Form(None),
    appointmentTypeID: Optional[str] = Form(None),
    mock: Optional[bool] = Form(False),
    db: Session = Depends(get_db)
):
    print(f"Received webhook: Action={action}, ID={id}, Calendar={calendarID}, Type={appointmentTypeID}")

    if calendarID != settings.calendar_id:
        return {"status": "passed", "message": f"Invalid calendar ID: {calendarID}"}
    
    # Validate the action type
    valid_actions = {"scheduled", "rescheduled", "canceled", "changed", "order.completed"}
    if action not in valid_actions:
        return {"status": "error", "message": f"Invalid action: {action}"}
    
    try:
        
        # Check if appointment exists
        try: 
            q = select(Appointment).where(Appointment.id == id)
            existing_appt = db.scalars(q).all()[0]
        except:
            existing_appt = None
        
        # Fetch appointment details from Acuity API
        try:
            appt_details: AcuityAppointment = acuity_client.get_appointment(id, mock=mock)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch appointment details: {str(e)}")
        

        old_time = None
        new_time = None
        event = None
        if not existing_appt:
            old_time = None
            new_time = datetime.fromisoformat(appt_details['datetime'])
            res = createNewAppointment(appt_details, db)
            event = Event(
                action=EventAction.schedule,
                old_time=old_time,
                new_time=new_time,
                appointment_id=res.id
            )
        elif appt_details['canceled']:
            old_time = existing_appt.start_time
            res = markAsSoftDelete(existing_appt, db)
            event = Event(
                action=EventAction.cancel,
                old_time=old_time,
                appointment_id=existing_appt.id
            )            
        elif isToday(appt_details['datetime']):
            new_time = datetime.fromisoformat(appt_details['datetime'])
            if isToday(existing_appt.start_time):
                old_time = existing_appt.start_time
                res = updateStartTime(existing_appt, new_time, db)
                event = Event(
                    action=EventAction.reschedule_same_day,
                    old_time=old_time,
                    new_time=new_time,
                    appointment_id=existing_appt.id
                )
            else:
                old_time = existing_appt.start_time
                new_time = datetime.fromisoformat(appt_details['datetime'])
                res = markAsSoftDelete(existing_appt, db)
                event = Event(
                    action=EventAction.reschedule_incoming,
                    old_time=old_time,
                    new_time=new_time,
                    appointment_id=existing_appt.id
                )
        elif not isToday(appt_details['datetime']):
            old_time = existing_appt.start_time
            new_time = datetime.fromisoformat(appt_details['datetime'])
            res = markAsSoftDelete(existing_appt, db)
            event = Event(
                action=EventAction.reschedule_outgoing,
                old_time=old_time,
                new_time=new_time,
                appointment_id=existing_appt.id
            )
        else:
            raise Exception("existing appt - Shouldn't end up here")
        
        db.add(event)
        db.commit()
        
        return {
            "status": "success", 
            "data": event
            }
            
    except Exception as e:
        # db.rollback()
        traceback.print_exc()
        print(str(e))
        return {"status": "error", "message": str(e)}



@router.post("/mock")
def mock_webhook(
    action: str = Form(...),
    id: str = Form(...),
    calendarID: Optional[str] = Form(None),
    appointmentTypeID: Optional[str] = Form(None),
    db: Session = Depends(get_db)):

    return handle_appt_changed(action, id, calendarID, appointmentTypeID, mock=True)