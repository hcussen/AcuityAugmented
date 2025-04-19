from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
import requests

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
    
    try:
        # Check if appointment exists
        existing_appt = db.query(Appointment).filter_by(id=id).first()
        
        # Fetch appointment details from Acuity API
        try:
            appt_details = acuity_client.get_appointment('1451596598')
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch appointment details: {str(e)}")
        
        # TODO: Process appointment details as needed
        print(appt_details)
        return {"status": "success", "message": f"Processed {action} for appointment {id}", "details": appt_details}
            
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}