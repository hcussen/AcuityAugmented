from app.types import AcuityAppointment
from sqlalchemy import update
from datetime import datetime 
from app.models import Appointment
from app.core.type_conversion import acuity_to_appointment

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
    newAppt = AcuityAppointment(**appt)
    db_appointment = acuity_to_appointment(newAppt)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def updateStartTime(appt: Appointment, newStart: datetime, db):
    q = update(Appointment)\
            .where(Appointment.id == appt.id)\
            .values(start_time=newStart)\
            .returning(Appointment.id, Appointment.start_time)
    res = db.execute(q)
    result = res.first()
    db.commit()
    return result

def markAsCanceled(appt: Appointment, db):
    q = update(Appointment)\
            .where(Appointment.id == appt.id)\
            .values(is_canceled=True)\
            .returning(Appointment.id, Appointment.is_canceled)
    res = db.execute(q)
    result = res.first()
    db.commit()
    return result