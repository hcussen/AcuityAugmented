from datetime import datetime, timedelta
from typing import Tuple
from zoneinfo import ZoneInfo
from app.config import settings

def get_today_boundaries(in_utc = True) -> Tuple[datetime, datetime, int]:
    # Get current time in local timezone (Mountain Time)
    local_tz = ZoneInfo('America/Denver')
    now = datetime.now(local_tz)
    
    # Create local midnight timestamps
    today_start = datetime(now.year, now.month, now.day, tzinfo=local_tz)
    today_end = today_start + timedelta(days=1)
    
    # Convert to UTC for database query
    today_start_utc = today_start.astimezone(ZoneInfo('UTC'))
    today_end_utc = today_end.astimezone(ZoneInfo('UTC'))
    
    today_day_of_week = now.weekday()
    return today_start_utc, today_end_utc, today_day_of_week

def get_center_opening_hours(day_of_week = None, in_utc = True) -> Tuple[datetime, datetime]:
    local_tz = ZoneInfo('America/Denver')
    now = datetime.now(local_tz)
    date = datetime.strftime(now, '%d/%m/%y')

    if day_of_week is None:
        day_of_week = now.weekday()

    center_open, center_close = settings.hours_open[day_of_week]
    center_open = datetime.strptime(f'{date} {center_open}', "%d/%m/%y %H:%M").replace(tzinfo=local_tz)
    center_close = datetime.strptime(f'{date} {center_close}', "%d/%m/%y %H:%M").replace(tzinfo=local_tz)
    print(center_open, center_close)
    if in_utc:
        center_open = center_open.astimezone(ZoneInfo('UTC'))
        center_close = center_close.astimezone(ZoneInfo('UTC'))
    print(center_open, center_close)
    return (center_open, center_close)

def isToday(timestamp_string: str) -> bool:
    '''takes in a date in the format 2025-06-03T19:00:00-0600'''
    # Parse the input timestamp
    timestamp = datetime.fromisoformat(str(timestamp_string))
    
    # Get today's date
    today = datetime.now()
    
    # Compare year, month, and day
    return (timestamp.year == today.year and
            timestamp.month == today.month and
            timestamp.day == today.day)
