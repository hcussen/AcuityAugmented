from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Tuple, Optional
from sqlalchemy import and_, or_
from uuid import UUID
from zoneinfo import ZoneInfo

from app.config import settings
from app.core.auth import get_api_key
from app.database import get_db
from app.models import Appointment, Event, EventAction
from app.core.time_utils import get_today_boundaries, get_center_opening_hours

from logging import getLogger
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


@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/healthcheck")
def read_root():
     return {"status": "ok"}

@router.get("/protected-endpoint")
async def protected_endpoint(api_key: str = Depends(get_api_key)):
    return {"message": "You have access to the protected endpoint"}


@router.post("/appointment")
def create_appointment(appt: AppointmentCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
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
def get_schedule(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    try:
        today_start, today_end, _ = get_today_boundaries()
        # Get appointments from database (they're in UTC)
        appointments = (
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
        # Convert timestamps to Mountain Time
        local_tz = ZoneInfo('America/Denver')
        for appt in appointments:
            # Add UTC timezone info to the naive datetime
            utc_start = appt.start_time.replace(tzinfo=ZoneInfo('UTC'))
            utc_created = appt.acuity_created_at.replace(tzinfo=ZoneInfo('UTC'))
            
            # Convert to local time
            appt.start_time = utc_start.astimezone(local_tz)
            appt.acuity_created_at = utc_created.astimezone(local_tz)
            
            if appt.acuity_deleted_at:
                utc_deleted = appt.acuity_deleted_at.replace(tzinfo=ZoneInfo('UTC'))
                appt.acuity_deleted_at = utc_deleted.astimezone(local_tz)
        
        return appointments

    except Exception as e:
        logger.error(f"Error in get_schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


def _initialize_hourly_diffs(day_of_week: int) -> Dict[str, HourlyDiff]:
    hourly_diffs: Dict[str, HourlyDiff] = {}
    center_open, center_close = get_center_opening_hours(day_of_week, in_utc=False)
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
def get_schedule_diff(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)) -> List[HourlyDiff]:
    try:
        # NOTE: the Events are in Local (Denver) time, but appointments are in utc (wtf)
        center_open, center_close = get_center_opening_hours()
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
                    # the event was created during center open hours, after the snapshot
                    Event.created_at >= center_open - timedelta(minutes=30), 
                    Event.created_at < center_close, 
                    # and the event applies to today 
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
