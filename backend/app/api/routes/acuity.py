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
import json 


router = APIRouter(
    prefix="/acuity",
    tags=["acuity"]
)

@router.get("/snapshot")
def take_snapshot(db: Session = Depends(get_db)):
    try: 
        appointments: List[AcuityAppointment] = acuity_client.get_appointments()
        snapshot = Snapshot(
            dump=json.dumps(appointments)
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return {"message": "Snapshot taken successfully", "count": len(appointments)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
