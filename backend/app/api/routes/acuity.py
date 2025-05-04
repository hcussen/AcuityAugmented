from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime 

from app.core.acuityClient import acuity_client
from app.core.type_conversion import acuity_to_appointment
from app.database import get_db
from app.models import Appointment, Snapshot

router = APIRouter(
    prefix="/acuity",
    tags=["acuity"]
)

@router.get("/appointment")
def get_acuity_appointment(id: str):
    return acuity_client.get_appointment(id)

@router.post("/snapshot")
def take_snapshot(db: Session = Depends(get_db)):
    try: 
        appointments = acuity_client.get_appointments()
        
        # Create snapshot record
        snapshot = Snapshot(
            dump=appointments
        )
        db.add(snapshot)
        
        # Get all Acuity IDs from the current API response
        current_acuity_ids = {appt['id'] for appt in appointments}
        
        # Find and delete appointments that no longer exist in Acuity
        deleted_count = db.query(Appointment).filter(
            and_(
                Appointment.acuity_id.notin_(current_acuity_ids),
                Appointment.is_canceled == True,
                Appointment.start_time < datetime.now(),
            )
        ).delete(synchronize_session=False)
        
        # Create individual appointment records
        for appt_data in appointments:
            # Convert to AcuityAppointment type for validation
            acuity_appt = AcuityAppointment(**appt_data)
            
            # Check if appointment already exists
            existing_appt = db.query(Appointment).filter(
                Appointment.acuity_id == acuity_appt.id
            ).first()
            
            if existing_appt:
                # Update existing appointment if needed
                existing_appt.start_time = datetime.fromisoformat(acuity_appt.datetime)
                existing_appt.is_canceled = acuity_appt.canceled
                existing_appt.last_modified_here = datetime.now()
            else:
                # Create new appointment
                new_appt = acuity_to_appointment(acuity_appt)
                db.add(new_appt)

        db.commit()
        db.refresh(snapshot)
        return {
            "message": "Snapshot and appointments saved successfully",
            "count": len(appointments),
            "deleted_count": deleted_count
        }

    except Exception as e:
        db.rollback()  # Rollback any changes if there's an error
        import traceback
        stack_trace = traceback.format_exc()
        raise HTTPException(status_code=400, detail={"error": str(e), "stack_trace": stack_trace})
