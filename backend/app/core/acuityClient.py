from base64 import b64encode
import requests
from app.types import AcuityAppointment
from typing import List 
from datetime import datetime

from app.config import settings

class AcuityClient:
    def __init__(self):
        self.base_url = "https://acuityscheduling.com/api/v1"
        auth = b64encode(f"{settings.acuity_user_id}:{settings.acuity_api_key}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {auth}',
            "accept": "application/json",
            "content-type": "application/json"  
        }
        self.appt_types = {
            'dummy': 42677283
        }
    
    def get_appointment(self, appointment_id: str) -> AcuityAppointment:
        """Fetch appointment details from Acuity API
        
        Args:
            appointment_id: The ID of the appointment to fetch
            
        Returns:
            Dict containing the appointment details
        """
        response = requests.get(
            f"{self.base_url}/appointments/{appointment_id}",
            headers=self.headers
        )
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()

    def get_appointments(self, today: bool = True, limit: int = 100) -> List[AcuityAppointment]:
        minDate, maxDate = None, None
        if today:
            todayDate = datetime.today().date()
            minDate, maxDate = todayDate, todayDate
        
        params = {
            'calendarID': settings.calendar_id,
            'minDate': minDate,
            'maxDate': maxDate
        }
        if limit:
            params['max'] = limit

        response = requests.get(
            f"{self.base_url}/appointments",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()
    
    def get_openings(self, appt_type: int, date: str = None, today: bool = True) -> List[dict]:
        
        if today and not date:
            date = datetime.today().date()

        params = {
            'calendarID': settings.calendar_id,
            "date": date,
            "appointmentTypeID": appt_type
        }

        response = requests.get(f"{self.base_url}/availability/times",
            headers=self.headers,
            params=params
        )

        response.raise_for_status()
        return response.json()
    
    def create_appointment(self, datetime: str, appt_type: int, first_name: str, last_name: str, email: str = '') -> dict:
        body = {
            'datetime': datetime,
            'appointmentTypeID': appt_type,
            'calendarID': settings.calendar_id,
            'firstName': first_name,
            'lastName': last_name,
            'email': email
        }
        response = requests.post(
            f"{self.base_url}/appointments",
            headers=self.headers,
            json=body,
            params={'admin': 'true'}
        )

        response.raise_for_status()
        return response.json()


# Create a singleton instance
acuity_client = AcuityClient()