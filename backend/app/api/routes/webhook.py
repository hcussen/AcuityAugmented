from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests
from datetime import datetime 

import traceback

from app.core.acuityClient import acuity_client

from app.database import get_db
from app.models import Appointment
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
        
        res = ''
        action_taken = ''
        direction = ''
        if not existing_appt:
            if isToday(appt_details['datetime']) and not appt_details['canceled']:
                action_taken = 'schedule'
                direction = 'null->today'
                res = createNewAppointment(appt_details, db)
            elif isToday(appt_details['datetime']) and appt_details['canceled']:
                # else if changed to canceled and original time was today:
                #   decision point: either ignore or add with canceled status
                #   this is relevant if you are starting from no appts
                action_taken = 'cancel'
                direction = "today->null"
                res = createNewAppointment(appt_details, db)
            else:
                action_taken = 'ignored'
                direction = 'null->null'
                res = {'datetime': appt_details['datetime'], 'canceled': appt_details['canceled'] }
        else:
            if appt_details['canceled']:
                action_taken = 'cancel'
                direction =  'today->null'
                res = markAsSoftDelete(existing_appt, db)
            elif isToday(appt_details['datetime']):
                action_taken = 'reschedule'
                direction = 'today->today'
                res = updateStartTime(existing_appt, datetime.fromisoformat(appt_details['datetime']), db)
            elif not isToday(appt_details['datetime']):
                action_taken = 'reschedule'
                direction = 'today->otherday'
                res = markAsSoftDelete(existing_appt, db)
            else:
                raise Exception("existing appt - Shouldn't end up here")
        
        return {
            "status": "success", 
            "data": { 
                "action_taken": f'{action_taken}',
                "direction": f'{direction}',
                "appt_id": f'{id}',
                "changed_fields": f"{res}"
                }
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