import pytest
from app.core.acuityClient import AcuityClient, acuity_client
from typing import List, Dict, Any
from app.types import AcuityAppointment, BaseAcuityAppointment
from app.models import Appointment
from copy import deepcopy


class MockAcuityClient:
    def __init__(self):
        # In-memory database of appointments
        self.appointments: List[BaseAcuityAppointment] = []
        
    def add_appointment(self, appointment_data: BaseAcuityAppointment) -> BaseAcuityAppointment:
        """Add a test appointment to the mock database"""

        # Make sure we have an ID
        if "id" not in appointment_data:
            # Generate a simple ID if none provided
            max_id = max([a.get("id", 0) for a in self.appointments], default=12345)
            appointment_data["id"] = max_id + 1
        
        # Add to our in-memory database
        self.appointments.append(deepcopy(appointment_data))
        return deepcopy(appointment_data)
    
    def get_appointment(self, appointment_id: str, mock: bool = False) -> Dict[str, Any]:
        """Get an appointment by ID"""
        # Convert to int if it's a string
        try:
            appointment_id = int(appointment_id)
        except ValueError:
            pass
            
        # Find matching appointment
        for appointment in self.appointments:
            if appointment.get("id") == appointment_id:
                return deepcopy(appointment)
        
        # If not found, raise an error like the real API would
        raise Exception(f"Appointment {appointment_id} not found")
    
    def get_appointments(self, today: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all appointments with optional filtering"""
        # In a real implementation, you might want to implement the date filtering
        # But for a basic mock, we'll just return all appointments
        result = deepcopy(self.appointments)
        
        # Apply limit if specified
        if limit and limit < len(result):
            result = result[:limit]
            
        return result
    
    def remove_appointment(self, appointment_id: str) -> None:
        """Remove an appointment by ID"""
        self.appointments = [a for a in self.appointments if a.get("id", '') != appointment_id]

    def clear_appointments(self):
        """Clear all test appointments"""
        self.appointments = []