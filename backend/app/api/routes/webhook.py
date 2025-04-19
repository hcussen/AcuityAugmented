from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import requests
from datetime import datetime 

import traceback

from app.core.acuityClient import acuity_client

from app.database import get_db
from app.models import Appointment

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/appt_changed")
async def handle_appt_changed(
    action: str = Form(...),
    id: str = Form(...),
    calendarID: Optional[str] = Form(None),
    appointmentTypeID: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    print(f"Received webhook: Action={action}, ID={id}, Calendar={calendarID}, Type={appointmentTypeID}")
    
    # Validate the action type
    valid_actions = {"scheduled", "rescheduled", "canceled", "changed", "order.completed"}
    if action not in valid_actions:
        return {"status": "error", "message": f"Invalid action: {action}"}
    
    return {"status": "well you got here at least"}

def isToday(timestamp_string):
    '''takes in a date in the format 2025-06-03T19:00:00-0600'''
    # Parse the input timestamp
    timestamp = datetime.fromisoformat(timestamp_string)
    
    # Get today's date
    today = datetime.now()
    
    # Compare year, month, and day
    return (timestamp.year == today.year and
            timestamp.month == today.month and
            timestamp.day == today.day)

def updateStartTime(appt: Appointment, newStart: datetime, db):
    print(newStart, type(newStart))
    q = update(Appointment)\
            .where(Appointment.id == appt.id)\
            .values(start_time=newStart)\
            .returning(Appointment.id, Appointment.start_time)
    print('-'*60)
    # print(q.compile(compile_kwargs={"literal_binds": True}))
    print('-'*60)
    res = db.execute(q)
    result = res.first()
    db.commit()
    return result

def markAsSoftDelete(appt: Appointment, db):
    q = update(Appointment)\
            .where(Appointment.id == appt.id)\
            .values(is_deleted=True)\
            .returning(Appointment.id, Appointment.is_deleted)
    res = db.execute(q)
    result = res.first()
    db.commit()
    return result


@router.post("/mock")
def mock_webhook(
    action: str = Form(...),
    id: str = Form(...),
    calendarID: Optional[str] = Form(None),
    appointmentTypeID: Optional[str] = Form(None),
    db: Session = Depends(get_db)):
    try:
        # Check if appointment exists
        print(id)
        q = select(Appointment).where(Appointment.id == id)
        existing_appt = db.scalars(q).all()[0]
        
        print('existing:', existing_appt)
        # Fetch appointment details from Acuity API
        try:
            pass 
            appt_details: AcuityAppointment = acuity_client.get_appointment(id, mock=True)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch appointment details: {str(e)}")
        
        # TODO: Process appointment details as needed
        print('acuity:', appt_details)
        
        res = ''
        action_taken = ''
        direction = ''
        if existing_appt:
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