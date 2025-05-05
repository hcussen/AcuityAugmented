import pytest
from datetime import datetime
from app.models import Appointment, Snapshot
from sqlalchemy import select
from freezegun import freeze_time
from app.config import settings
from app.core.type_conversion import acuity_to_appointment
from app.types import AcuityAppointment


def create_appointment_details(num) -> AcuityAppointment:
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
        "appointmentTypeID": 123456789,
        "classID": None,
        "addonIDs": [],
        "category": "",
        "duration": "60",
        "calendar": "Seattle Grace General Surgery",
        "calendarID": settings.calendar_id,
        "certificate": None,
        "confirmationPage": "this_is_a_URL",
        "confirmationPagePaymentLink": "this_is_a_URL",
        "location": "An Address",
        "notes": "",
        "timezone": "America/Seattle",
        "calendarTimezone": "America/Seattle",
        "canceled": False,
        "canClientCancel": True,
        "canClientReschedule": True,
        "labels": None,
        "forms": [],
        "formsText": "beepboop",
        "isVerified": False,
        "scheduledBy": "example@graysloanmemorial.com"
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
        response = test_client.post('/acuity/snapshot')
        
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

    @freeze_time("2025-04-26")
    def test_multiple_snapshots(self, db_session, test_client, patched_acuity_client):
        # First snapshot with initial appointments
        initial_appointments = [
            create_appointment_details(0),
            create_appointment_details(1),
        ]
        
        for appt in initial_appointments:
            patched_acuity_client.add_appointment(appt)

        # Take first snapshot
        response = test_client.post('/acuity/snapshot')
        assert response.status_code == 200
        content = response.json()
        assert content["count"] == 2
        
        # Verify first snapshot
        snapshots = db_session.query(Snapshot).all()
        assert len(snapshots) == 1
        assert len(snapshots[0].dump) == 2

        # Add new appointments
        new_appointments = [
            create_appointment_details(2),
            create_appointment_details(3),
            create_appointment_details(4),
        ]
        
        for appt in new_appointments:
            patched_acuity_client.add_appointment(appt)

        # Take second snapshot
        response = test_client.post('/acuity/snapshot')
        assert response.status_code == 200
        content = response.json()
        assert content["count"] == 5  # Should now have all 5 appointments
        
        # Verify snapshots
        snapshots = db_session.query(Snapshot).all()
        assert len(snapshots) == 2  # Should now have 2 snapshots
        assert len(snapshots[1].dump) == 5  # Latest snapshot should have all appointments
        
        # Verify all appointments exist in database
        appointments = db_session.query(Appointment).all()
        assert len(appointments) == 5
        
        # Verify each appointment exists and has correct details
        all_appointments = initial_appointments + new_appointments
        for appt_data in all_appointments:
            appointment = db_session.query(Appointment).filter(
                Appointment.acuity_id == appt_data["id"]
            ).first()
            
            assert appointment is not None
            assert appointment.first_name == appt_data["firstName"]
            assert appointment.last_name == appt_data["lastName"]
            assert appointment.start_time == datetime.fromisoformat(appt_data["datetime"]).replace(tzinfo=None)
            assert appointment.duration == int(appt_data["duration"])
            assert appointment.is_canceled == appt_data["canceled"]

    @freeze_time("2025-04-25")
    def test_appointments_deleted_when_not_in_api(self, db_session, test_client, patched_acuity_client):
        """Test that appointments not present in the API response and with start_time today or earlier are deleted"""
        
        # Create initial appointments in the database
        initial_appointments = [
            create_appointment_details(0),
            create_appointment_details(1),
            create_appointment_details(2),
        ]
        
        for appt in initial_appointments:
            db_session.add(acuity_to_appointment(AcuityAppointment(**appt)))
        db_session.commit()

        # confirm that the appts were created in db 
        appointments = db_session.query(Appointment).all()
        assert len(appointments) == 3

        # Mock the Acuity API to return only one appointment (ID 12345)
        mock_api_response = [create_appointment_details(0)]
        for appt in mock_api_response:
            patched_acuity_client.add_appointment(appt)

        # Take a new snapshot
        response = test_client.post('/acuity/snapshot')
        
        assert response.status_code == 200
        content = response.json()
        print(content)
        assert content["deleted_count"] == 2  # Two appointments should be deleted (ID 12346 and 12347)
        
        # Verify the right appointments remain
        remaining_appointments = db_session.query(Appointment).order_by(Appointment.acuity_id).all()
        assert len(remaining_appointments) == 1
        assert [a.acuity_id for a in remaining_appointments] == [12345]  # Today's kept appt and future appt

    @freeze_time("2025-04-26")
    def test_no_appointments_deleted_when_all_present(self, db_session, test_client, patched_acuity_client):
        """Test that no appointments are deleted when all are present in API response"""
        
        # Create initial appointments in the database
        initial_appointments = [
            Appointment(
                acuity_id=12345,
                first_name="Keep",
                last_name="One",
                start_time=datetime.fromisoformat("2025-04-26T10:00:00-0600"),  # Today
                is_canceled=False,
                last_modified_here=datetime.now()
            ),
            Appointment(
                acuity_id=12346,
                first_name="Keep",
                last_name="Two",
                start_time=datetime.fromisoformat("2025-04-26T14:00:00-0600"),  # Today
                is_canceled=False,
                last_modified_here=datetime.now()
            )
        ]
        
        for appt in initial_appointments:
            db_session.add(appt)
        db_session.commit()

        # Mock the Acuity API to return both appointments
        mock_api_response = [create_appointment_details(0), create_appointment_details(1)]
        for appt in mock_api_response:
            patched_acuity_client.add_appointment(appt)

        # Take a new snapshot
        response = test_client.post('/acuity/snapshot')
        
        assert response.status_code == 200
        content = response.json()
        assert content["deleted_count"] == 0  # No appointments should be deleted
        
        # Verify both appointments still exist
        remaining_appointments = db_session.query(Appointment).order_by(Appointment.acuity_id).all()
        assert len(remaining_appointments) == 2
        assert [a.acuity_id for a in remaining_appointments] == [12345, 12346]

    @freeze_time("2025-04-26")
    def test_future_appointments_not_deleted(self, db_session, test_client, patched_acuity_client):
        """Test that future appointments are not deleted even if missing from API"""
        
        # Create initial appointments in the database
        initial_appointments = [
            Appointment(
                acuity_id=12345,
                first_name="Today",
                last_name="Appt",
                start_time=datetime.fromisoformat("2025-04-26T14:00:00-0600"),  # Today
                is_canceled=False,
                last_modified_here=datetime.now()
            ),
            Appointment(
                acuity_id=12346,
                first_name="Future",
                last_name="Appt",
                start_time=datetime.fromisoformat("2025-04-27T14:00:00-0600"),  # Tomorrow
                is_canceled=False,
                last_modified_here=datetime.now()
            )
        ]
        
        for appt in initial_appointments:
            db_session.add(appt)
        db_session.commit()

        # Mock the Acuity API to return no appointments
        mock_api_response = []
        
        # Take a new snapshot
        response = test_client.post('/acuity/snapshot')
        
        assert response.status_code == 200
        content = response.json()
        assert content["deleted_count"] == 1  # Only today's appointment should be deleted
        
        # Verify only future appointment remains
        remaining_appointments = db_session.query(Appointment).all()
        assert len(remaining_appointments) == 1
        assert remaining_appointments[0].acuity_id == 12346  # Future appointment

    @freeze_time("2025-04-26")
    def test_snapshot_with_updates(self, db_session, test_client, patched_acuity_client):
        # First snapshot with initial appointments
        initial_appointments = [
            create_appointment_details(0),
            create_appointment_details(1),
        ]
        
        for appt in initial_appointments:
            patched_acuity_client.add_appointment(appt)

        # Take first snapshot
        response = test_client.post('/acuity/snapshot')
        assert response.status_code == 200
        content = response.json()
        assert content["count"] == 2
        
        # Verify first snapshot
        snapshots = db_session.query(Snapshot).all()
        assert len(snapshots) == 1
        assert len(snapshots[0].dump) == 2
        
        # Verify first snapshot contains original appointment data
        snapshot_appointments = snapshots[0].dump
        assert any(appt["id"] == 12345 and appt["datetime"] == "2025-04-25T19:00:00-0600" 
                  for appt in snapshot_appointments)

        # Modify one appointment (change time and add a note)
        modified_appt = create_appointment_details(0)  # Get the base appointment
        modified_appt["datetime"] = "2025-04-25T21:00:00-0600"  # Change from 19:00 to 21:00
        modified_appt["notes"] = "Rescheduled appointment"
        modified_appt["time"] = "9:00pm"
        modified_appt["endTime"] = "10:00pm"

        patched_acuity_client.remove_appointment(create_appointment_details(0)['id'])
        patched_acuity_client.add_appointment(modified_appt)  # This will override the existing one
        
        # Add a new appointment and update the modified one
        new_appointment = create_appointment_details(2)
        patched_acuity_client.add_appointment(new_appointment)  
        
        # Take second snapshot
        response = test_client.post('/acuity/snapshot')
        assert response.status_code == 200
        content = response.json()
        assert content["count"] == 3
        
        # Verify snapshots
        snapshots = db_session.query(Snapshot).all()
        assert len(snapshots) == 2
        assert len(snapshots[1].dump) == 3
        
        # Verify second snapshot contains updated appointment data
        snapshot_appointments = snapshots[1].dump
        assert any(appt["id"] == 12345 and appt["datetime"] == "2025-04-25T21:00:00-0600" 
                  and appt["notes"] == "Rescheduled appointment"
                  for appt in snapshot_appointments)
        
        # Verify the modified appointment was updated in the database
        modified_appointment = db_session.query(Appointment).filter(
            Appointment.acuity_id == modified_appt["id"]
        ).first()
        
        assert modified_appointment is not None
        assert modified_appointment.start_time == datetime.fromisoformat("2025-04-25T21:00:00-0600").replace(tzinfo=None)
        
        # Verify all appointments exist with correct details
        all_appointments = [modified_appt, initial_appointments[1], new_appointment]
        for appt_data in all_appointments:
            appointment = db_session.query(Appointment).filter(
                Appointment.acuity_id == appt_data["id"]
            ).first()
            
            assert appointment is not None
            assert appointment.first_name == appt_data["firstName"]
            assert appointment.last_name == appt_data["lastName"]
            assert appointment.start_time == datetime.fromisoformat(appt_data["datetime"]).replace(tzinfo=None)
            assert appointment.duration == int(appt_data["duration"])
            assert appointment.is_canceled == appt_data["canceled"]