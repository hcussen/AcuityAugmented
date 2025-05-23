from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

class BaseAcuityAppointment(BaseModel):
    """Base model with essential appointment fields"""
    id: int
    firstName: str
    lastName: str
    datetime: str  # ISO-like format "YYYY-MM-DDThh:mm:ss-zzzz"
    canceled: bool = False
    calendarID: int
    model_config = ConfigDict(extra='allow')

class AcuityAppointment(BaseAcuityAppointment):
    """
    Model representing an appointment from the Acuity Scheduling API.
    Based on the JSON structure from actual API responses.
    """
    phone: Optional[str] = None
    email: Optional[str] = None
    date: str  # Format "Month Day, Year" (e.g., "April 22, 2025")
    time: str  # Format "h:mmam/pm" (e.g., "7:00pm")
    endTime: str  # Format "h:mmam/pm" (e.g., "8:00pm")
    dateCreated: str  # Format "Month Day, Year" (e.g., "March 30, 2025")
    datetimeCreated: str  # ISO-like format "YYYY-MM-DDThh:mm:ss-zzzz" (e.g., "2025-03-30T12:51:40-0500")
    price: str  # Decimal price as string (e.g., "0.00")
    priceSold: str  # Decimal price as string (e.g., "0.00")
    paid: str  # "yes" or "no"
    amountPaid: str  # Decimal amount as string (e.g., "0.00")
    type: str  # Appointment type name (e.g., "Tutor Session")
    appointmentTypeID: int
    classID: Optional[int] = None
    addonIDs: List[int] = Field(default_factory=list)
    category: str = ""
    duration: str  # Duration in minutes as string (e.g., "60")
    calendar: str
    certificate: Optional[str] = None
    confirmationPage: str  # URL to confirmation page
    confirmationPagePaymentLink: str  # URL to payment confirmation page
    location: str
    notes: str = ""
    timezone: str
    calendarTimezone: str
    canClientCancel: bool = False
    canClientReschedule: bool = False
    labels: Optional[Union[str, List[str]]] = None
    forms: List = Field(default_factory=list)  # This could be further defined if needed
    formsText: str

    model_config = ConfigDict(extra='allow')