from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests
from datetime import datetime 

import traceback
from typing import List 
from app.core.acuityClient import acuity_client
from app.types import AcuityAppointment
from app.database import get_db
from app.models import Appointment, Snapshot
from app.core.apptActions import isToday, createNewAppointment, updateStartTime, markAsSoftDelete
from sqlalchemy.dialects.sqlite import JSON


router = APIRouter(
    prefix="/acuity",
    tags=["acuity"]
)

@router.get("/snapshot")
def take_snapshot(db: Session = Depends(get_db)):
    try: 
        appointments = acuity_client.get_appointments(limit=5)
        snapshot = Snapshot(
            dump=appointments  # SQLAlchemy will handle JSON serialization via the JSON type
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return {"message": "Snapshot taken successfully", "count": len(appointments)}

    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        raise HTTPException(status_code=400, detail={"error": str(e), "stack_trace": stack_trace})
