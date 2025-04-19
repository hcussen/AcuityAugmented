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

def createNewAppointment(appt: AcuityAppointment, db):
    db_appointment = Appointment(
        id=appt['id'],
        first_name=appt['firstName'],
        last_name=appt['lastName'],
        start_time=datetime.fromisoformat(appt['datetime']),
        duration=appt['duration'],
        acuity_created_at=datetime.fromisoformat(appt['datetimeCreated']),
        is_deleted=appt['canceled']
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

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