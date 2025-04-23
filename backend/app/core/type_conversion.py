from datetime import datetime
from app.types import AcuityAppointment
from app.models import Appointment

def acuity_to_appointment(acuity_appt: AcuityAppointment) -> Appointment:
    """
    Convert an AcuityAppointment to an Appointment model.
    
    Args:
        acuity_appt (AcuityAppointment): The Acuity appointment data
        
    Returns:
        Appointment: A new Appointment instance with data from the Acuity appointment
    """
    return Appointment(
        acuity_id=acuity_appt.id,
        first_name=acuity_appt.firstName,
        last_name=acuity_appt.lastName,
        start_time=datetime.fromisoformat(acuity_appt.datetime),
        duration=int(acuity_appt.duration),
        acuity_created_at=datetime.fromisoformat(acuity_appt.datetimeCreated),
        is_canceled=acuity_appt.canceled
    )
