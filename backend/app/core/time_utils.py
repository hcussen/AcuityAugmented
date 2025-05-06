from datetime import datetime, timedelta
from typing import Tuple
from app.config import settings

def get_today_boundaries() -> Tuple[datetime, datetime, int]:
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    today_end = today_start + timedelta(days=1)
    today_day_of_week = now.weekday()
    return today_start, today_end, today_day_of_week

def get_center_opening_hours(day_of_week = None) -> Tuple[datetime, datetime]:
    now = datetime.now()
    date = datetime.strftime(now, '%d/%m/%y')

    if day_of_week is None:
        day_of_week = now.weekday()

    center_open, center_close = settings.hours_open[day_of_week]
    center_open = datetime.strptime(f'{date} {center_open}', "%d/%m/%y %H:%M")
    center_close = datetime.strptime(f'{date} {center_close}', "%d/%m/%y %H:%M")
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
