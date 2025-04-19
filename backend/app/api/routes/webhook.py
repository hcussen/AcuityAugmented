from fastapi import APIRouter, Request, Form, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

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
        
        if not existing_appt:
            match action:
                case "scheduled":
                    pass
                case _:
                    return {"status": "error", "message": f"Invalid action: {action}"}
        else:
            match action:
                case "scheduled":
                    pass
                case _:
                    return {"status": "error", "message": f"Invalid action: {action}"}
            
        return {"status": "success", "message": f"No action needed for {action}"}
            
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}