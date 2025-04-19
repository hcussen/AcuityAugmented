from base64 import b64encode
import requests
from typing import Dict, Any

from app.config import settings

class AcuityClient:
    def __init__(self):
        self.base_url = "https://acuityscheduling.com/api/v1"
        auth = b64encode(f"{settings.acuity_user_id}:{settings.acuity_api_key}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {auth}'
        }
    
    def get_appointment(self, appointment_id: str) -> Dict[str, Any]:
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

# Create a singleton instance
acuity_client = AcuityClient()