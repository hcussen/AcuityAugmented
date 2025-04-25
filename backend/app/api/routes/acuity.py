from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests
from datetime import datetime 

import traceback
from typing import List 
from app.core.acuityClient import get_acuity_client, AcuityClient
from app.core.type_conversion import acuity_to_appointment
from app.database import get_db
from app.models import Appointment, Snapshot
from sqlalchemy.dialects.sqlite import JSON


router = APIRouter(
    prefix="/acuity",
    tags=["acuity"]
)

@router.get("/snapshot")
def take_snapshot(db: Session = Depends(get_db), acuity: AcuityClient = Depends(get_acuity_client)):
    try: 
        appointments = acuity.get_appointments()
        
        # Create snapshot record
        snapshot = Snapshot(
            dump=appointments
        )
        db.add(snapshot)
        
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
        return {"message": "Snapshot and appointments saved successfully", "count": len(appointments)}

    except Exception as e:
        db.rollback()  # Rollback any changes if there's an error
        import traceback
        stack_trace = traceback.format_exc()
        raise HTTPException(status_code=400, detail={"error": str(e), "stack_trace": stack_trace})
