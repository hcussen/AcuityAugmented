import pytest
from datetime import datetime
from app.models import Appointment, Snapshot
from sqlalchemy import select
from freezegun import freeze_time


def create_appointment_details(num):
    return {
        "id": 12345 + num,
        "firstName": f"Meredith{num}",
        "lastName": f"Gray{num}",
        "phone": "",
        "email": "",
        "date": "April 25, 2025",
        "time": "7:00pm",
        "endTime": "8:00pm",
        "dateCreated": "April 24, 2025",
        "datetimeCreated": f"2025-04-24T19:00:00-0600",
        "datetime": f"2025-04-25T{19+num}:00:00-0600",
        "price": "0.00",
        "priceSold": "0.00",
        "paid": "no",
        "amountPaid": "0.00",
        "type": "Dummy Appt",
        "appointmentTypeID": 42677283,
        "classID": None,
        "addonIDs": [],
        "category": "",
        "duration": "60",
        "calendar": "Mathnasium of Aurora",
        "calendarID": 1574840,
        "certificate": None,
        "confirmationPage": "https://app.acuityscheduling.com/schedule.php?owner=14442476&action=appt&id%5B%5D=87c7fa149056bb797b7c4838b99bf7cb",
        "confirmationPagePaymentLink": "https://app.acuityscheduling.com/schedule.php?owner=14442476&action=appt&id%5B%5D=87c7fa149056bb797b7c4838b99bf7cb&paymentLink=true#payment",
        "location": "4510 S Reservoir Rd. Centennial, CO. 80015",
        "notes": "",
        "timezone": "America/Denver",
        "calendarTimezone": "America/Denver",
        "canceled": False,
        "canClientCancel": True,
        "canClientReschedule": True,
        "labels": None,
        "forms": [],
        "formsText": "Name: Dummy Apt\nPhone: \n\nLocation\n============\n4510 S Reservoir Rd. Centennial, CO. 80015\n",
        "isVerified": False,
        "scheduledBy": "aurora@mathnasium.com"
    }

class TestSnapshot:
    @freeze_time("2025-04-26")
    def test_snapshot_creates_appointments(self, db_session, test_client, patched_acuity_client):
        # Setup test appointments in mock Acuity client
        test_appointments = [
            create_appointment_details(0),
            create_appointment_details(1),
            create_appointment_details(2),
        ]

        # Add appointments to mock client
        for appt in test_appointments:
            patched_acuity_client.add_appointment(appt)

        # Call the snapshot endpoint
        response = test_client.get('/acuity/snapshot')
        
        # Verify response
        assert response.status_code == 200
        content = response.json()
        assert content["count"] == 3
        assert "Snapshot and appointments saved successfully" in content["message"]

        # Verify snapshot was created
        snapshots = db_session.query(Snapshot).all()
        assert len(snapshots) == 1
        assert len(snapshots[0].dump) == 3

        # Verify appointments were created
        appointments = db_session.query(Appointment).all()
        assert len(appointments) == 3

        # Verify specific appointment details
        for i, appt_data in enumerate(test_appointments):
            appointment = db_session.query(Appointment).filter(
                Appointment.acuity_id == appt_data["id"]
            ).first()
            
            assert appointment is not None
            assert appointment.first_name == appt_data["firstName"]
            assert appointment.last_name == appt_data["lastName"]
            assert appointment.start_time == datetime.fromisoformat(appt_data["datetime"]).replace(tzinfo=None)
            assert appointment.duration == int(appt_data["duration"])
            assert appointment.is_canceled == appt_data["canceled"]