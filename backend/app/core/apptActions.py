from app.types import AcuityAppointment
from sqlalchemy import update
from datetime import datetime 
from app.models import Appointment, Event, EventAction
from app.core.type_conversion import acuity_to_appointment

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
            .values(start_time=newStart)
    db.execute(q)
    db.commit()
    db.refresh(appt)
    return appt

def markAsCanceled(appt: Appointment, db):
    q = update(Appointment)\
            .where(Appointment.id == appt.id)\
            .values(is_canceled=True)
    db.execute(q)
    db.commit()
    # Refresh the appointment object
    db.refresh(appt)
    return appt

def handle_schedule(appt: AcuityAppointment, db) -> Event:
    old_time = None
    new_time = datetime.fromisoformat(appt['datetime']).replace(
        tzinfo=None
    )
    res = createNewAppointment(appt, db)
    event = Event(
        action=EventAction.schedule,
        old_time=old_time,
        new_time=new_time,
        appointment_id=res.id,
    )
    return event

def handle_cancel(existing_appt: Appointment, db) -> Event:
    old_time = existing_appt.start_time
    res = markAsCanceled(existing_appt, db)
    event = Event(
        action=EventAction.cancel,
        old_time=old_time,
        appointment_id=existing_appt.id,
    )
    return event

def handle_reschedule_same_day(existing_appt: Appointment, appt_details: AcuityAppointment, db) -> Event:
    old_time = existing_appt.start_time
    new_time = datetime.fromisoformat(appt_details['datetime']).replace(
        tzinfo=None
    )
    res = updateStartTime(existing_appt, new_time, db)
    event = Event(
        action=EventAction.reschedule_same_day,
        old_time=old_time,
        new_time=new_time,
        appointment_id=existing_appt.id,
    )
    return event

def handle_reschedule_incoming(existing_appt: Appointment, appt_details: AcuityAppointment, db) -> Event:
    old_time = existing_appt.start_time
    new_time = datetime.fromisoformat(appt_details['datetime']).replace(
        tzinfo=None
    )
    res = markAsCanceled(existing_appt, db)
    event = Event(
        action=EventAction.reschedule_incoming,
        old_time=old_time,
        new_time=new_time,
        appointment_id=existing_appt.id,
    )
    return event

def handle_reschedule_outgoing(existing_appt: Appointment, appt_details: AcuityAppointment, db) -> Event:
    old_time = existing_appt.start_time
    new_time = datetime.fromisoformat(appt_details['datetime']).replace(
        tzinfo=None
    )
    res = updateStartTime(existing_appt, new_time, db)
    event = Event(
        action=EventAction.reschedule_outgoing,
        old_time=old_time,
        new_time=new_time,
        appointment_id=existing_appt.id,
    )
    return event