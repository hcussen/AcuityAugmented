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
            'Authorization': f'Basic {auth}'
        }
    
    def get_appointment(self, appointment_id: str, mock: bool = False) -> AcuityAppointment:
        """Fetch appointment details from Acuity API
        
        Args:
            appointment_id: The ID of the appointment to fetch
            
        Returns:
            Dict containing the appointment details
        """
        if mock:
            return {
                "id": 1451596598,
                "firstName": "Dummy",
                "lastName": "Apt",
                "phone": "",
                "email": "",
                "date": "June 3, 2025",
                "time": "7:00pm",
                "endTime": "8:00pm",
                "dateCreated": "April 9, 2025",
                "datetimeCreated": "2025-04-09T17:15:16-0500",
                "datetime": "2025-04-19T19:00:00-0600",
                "price": "0.00",
                "priceSold": "0.00",
                "paid": "no",
                "amountPaid": "0.00",
                "type": "Dummy Appt",
                "appointmentTypeID": 42677283,
                #   "classID": null,
                "addonIDs": [],
                "category": "",
                "duration": "60",
                "calendar": "Mathnasium of Aurora",
                "calendarID": 1574840,
                #   "certificate": null,
                "confirmationPage": "https://app.acuityscheduling.com/schedule.php?owner=14442476&action=appt&id%5B%5D=87c7fa149056bb797b7c4838b99bf7cb",
                "confirmationPagePaymentLink": "https://app.acuityscheduling.com/schedule.php?owner=14442476&action=appt&id%5B%5D=87c7fa149056bb797b7c4838b99bf7cb&paymentLink=true#payment",
                "location": "4510 S Reservoir Rd. Centennial, CO. 80015",
                "notes": "",
                "timezone": "America/Denver",
                "calendarTimezone": "America/Denver",
                "canceled": True,
                "canClientCancel": True,
                "canClientReschedule": True,
                #   "labels": null,
                "forms": [],
                "formsText": "Name: Dummy Apt\nPhone: \n\nLocation\n============\n4510 S Reservoir Rd. Centennial, CO. 80015\n",
                "isVerified": False,
                "scheduledBy": "aurora@mathnasium.com"
                }
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
# Create a dependency provider
def get_acuity_client() -> AcuityClient:
    return AcuityClient()