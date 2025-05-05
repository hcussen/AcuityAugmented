from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Tuple, Optional
from sqlalchemy import and_, or_
from logging import getLogger
from uuid import UUID
import traceback

from app.config import settings
from app.database import get_db
from app.models import Appointment, Event, EventAction
from app.core.time_utils import get_today_boundaries

logger = getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["general"],
)


# Request model for appointment creation
class AppointmentCreate(BaseModel):
    id: str
    acuity_id: int
    first_name: str
    last_name: str
    start_time: datetime
    duration: int
    acuity_created_at: datetime

class SimpleEvent(BaseModel):
    id: UUID
    first_name: str
    last_name: str

class HourlyDiff(BaseModel):
    hour: str
    added: List[SimpleEvent] = []
    deleted: List[SimpleEvent] = []


@router.post("/appointment")
def create_appointment(appt: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        db_appointment = Appointment(
            id=appt.id,
            acuity_id=appt.acuity_id,
            first_name=appt.first_name,
            last_name=appt.last_name,
            start_time=appt.start_time,
            duration=appt.duration,
            acuity_created_at=appt.acuity_created_at,
        )
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/schedule")
def get_schedule(db: Session = Depends(get_db)):
    try:
        today_start, today_end, _ = get_today_boundaries()

        return (
            db.query(Appointment)
            .filter(
                and_(
                    Appointment.start_time >= today_start,
                    Appointment.start_time < today_end,
                )
            )
            .order_by(Appointment.start_time)
            .all()
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _initialize_hourly_diffs(day_of_week: int) -> Dict[str, HourlyDiff]:
    hourly_diffs: Dict[str, HourlyDiff] = {}
    center_open, center_close = settings.hours_open[day_of_week]
    center_open = datetime.strptime(center_open, "%H:%M")
    center_close = datetime.strptime(center_close, "%H:%M")
    hours_open = int((center_close - center_open).total_seconds() // 3600)
    
    for i in range(hours_open):
        hour = datetime.strftime(center_open + timedelta(hours=i), "%H:%M")
        hourly_diffs[hour] = HourlyDiff(hour=hour)
    return hourly_diffs


def _process_event(
    event: Event,
    first_name: str,
    last_name: str,
    hourly_diffs: Dict[str, HourlyDiff]
) -> None:
    old_hour = event.old_time.strftime("%H:%M") if event.old_time else None
    new_hour = event.new_time.strftime("%H:%M") if event.new_time else None
    
    simple_event = SimpleEvent(
        id=event.appointment_id,
        first_name=first_name,
        last_name=last_name,
    )
    
    try:
        match event.action:
            case EventAction.schedule:
                hourly_diffs[new_hour].added.append(simple_event)
            case EventAction.cancel:
                hourly_diffs[old_hour].deleted.append(simple_event)
            case EventAction.reschedule_same_day:
                hourly_diffs[old_hour].deleted.append(simple_event)
                hourly_diffs[new_hour].added.append(simple_event)
            case EventAction.reschedule_incoming:
                hourly_diffs[new_hour].added.append(simple_event)
            case EventAction.reschedule_outgoing:
                hourly_diffs[old_hour].deleted.append(simple_event)
            case _:
                logger.warning(f"Unknown action: {event.action} for id {event.id}")
    except Exception as e:
        logger.error(f"Error processing event {event.id}: {str(e)}")
        logger.debug(f"Event data: {event.to_dict()}")


@router.get("/schedule/diff", response_model=List[HourlyDiff])
def get_schedule_diff(db: Session = Depends(get_db)) -> List[HourlyDiff]:
    try:
        today_start, today_end, today_day_of_week = get_today_boundaries()
        
        today_events = (
            db.query(
                Event,
                Appointment.first_name,
                Appointment.last_name,
                Appointment.start_time,
            )
            .join(Event.appointment)
            .filter(
                and_(
                    Event.created_at >= today_start, 
                    Event.created_at < today_end, 
                    or_(Event.old_time <= today_end, Event.new_time <= today_end)
                ))
            .order_by(Event.created_at)
            .all()
        )

        hourly_diffs = _initialize_hourly_diffs(today_day_of_week)
        
        for event, first_name, last_name, _ in today_events:
            _process_event(event, first_name, last_name, hourly_diffs)
                
        return list(hourly_diffs.values())

    except Exception as e:
        logger.error(f"Error in get_schedule_diff: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
