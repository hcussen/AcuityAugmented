from datetime import datetime, timedelta
from typing import Tuple

def get_today_boundaries() -> Tuple[datetime, datetime, int]:
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    today_end = today_start + timedelta(days=1)
    today_day_of_week = now.weekday()
    return today_start, today_end, today_day_of_week


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
