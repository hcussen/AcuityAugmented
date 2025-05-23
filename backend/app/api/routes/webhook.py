from fastapi import APIRouter, Form, Depends, HTTPException
from typing import Optional
from app.types import AcuityAppointment
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests
from datetime import datetime
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)

from app.core.acuityClient import acuity_client

from app.database import get_db
from app.models import Appointment 
from app.core.apptActions import (
    handle_reschedule_same_day,
    handle_schedule,
    handle_cancel,
    handle_reschedule_incoming,
    handle_reschedule_outgoing,
)
from app.core.time_utils import isToday

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/appt-changed")
async def handle_appt_changed(
    action: str = Form(...),
    id: str = Form(...),
    calendarID: Optional[str] = Form(None),
    appointmentTypeID: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    logger.info(
        "Received webhook: Action=%s, ID=%s, Calendar=%s, Type=%s",
        action,
        id,
        calendarID,
        appointmentTypeID
    )

    if calendarID != settings.calendar_id:
        logger.warning("Invalid calendar ID received: %s", calendarID)
        return {"status": "passed", "message": f"Invalid calendar ID: {calendarID}"}

    # Validate the action type
    valid_actions = {
        "scheduled",
        "rescheduled",
        "canceled",
        "changed",
        "order.completed",
    }
    if action not in valid_actions:
        logger.error("Invalid action received: %s", action)
        return {"status": "error", "message": f"Invalid action: {action}"}

    try:

        # Check if appointment exists
        try:
            q = select(Appointment).where(Appointment.acuity_id == id)
            existing_appt = db.scalars(q).all()[0]
        except:
            existing_appt = None

        # Fetch appointment details from Acuity API
        try:
            appt_details: AcuityAppointment = acuity_client.get_appointment(id)
        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch appointment details: %s", str(e))
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch appointment details: {str(e)}"
            )

        event = None
        if not existing_appt and not isToday(appt_details["datetime"]):
                logger.info("Appt %s doesn't deal with today", id)
                return {
                    "status": "passed",
                    "message": f"Appt {id} doesn't deal with today",
                }
        elif not existing_appt and isToday(appt_details["datetime"]):
            event = handle_schedule(appt_details, db)
        elif appt_details["canceled"]:
            event = handle_cancel(existing_appt, db)
        elif isToday(appt_details["datetime"]) and isToday(existing_appt.start_time):
            event = handle_reschedule_same_day(existing_appt, appt_details, db)
        elif isToday(appt_details["datetime"]) and not isToday(existing_appt.start_time):
            # why this would happen, I'm not sure. But I'm handling it 
            event = handle_reschedule_incoming(existing_appt, appt_details, db)
        elif not isToday(appt_details["datetime"]):
            event = handle_reschedule_outgoing(existing_appt, appt_details, db)
        else:
            logger.error("Unexpected appointment state")
            raise Exception("existing appt - Shouldn't end up here")
        db.add(event)
        db.commit()

        logger.info("Webhook processed successfully")
        return {"status": "success", "data": json.dumps(event.to_dict())}

    except Exception as e:
        db.rollback()
        logger.error("Error processing webhook: %s", str(e), exc_info=True)
        return {"status": "error", "message": str(e)}
