# tests/test_webhook_appointments.py
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from app.models import Appointment, Event, EventAction
from app.config import settings

class TestAppointmentWebhooks:
    def test_database_connection(self, db_session):
        """Verify that the database connection works and tables are created"""
        # Try to create a simple appointment
        test_appt = Appointment(
            acuity_id=999,
            first_name="Test",
            last_name="User",
            start_time=datetime.now(),
            duration=60,
            acuity_created_at=datetime.now()
        )
        
        # Add and commit to database
        db_session.add(test_appt)
        db_session.commit()
        
        # Query it back
        queried_appt = db_session.query(Appointment).filter_by(acuity_id=999).first()
        assert queried_appt is not None
        assert queried_appt.first_name == "Test"
        assert queried_appt.last_name == "User"
        
        # Clean up
        db_session.delete(queried_appt)
        db_session.commit()
    
    # Helper method to verify event creation
    def _verify_event(self, db_session, appt_id, expected_action, expected_old_time=None, expected_new_time=None):
        event = db_session.query(Event).filter_by(appointment_id=appt_id).first()
        assert event is not None
        assert event.action == expected_action
        if expected_old_time:
            assert event.old_time == expected_old_time
        if expected_new_time:
            assert event.new_time == expected_new_time
        return event

    # 3. New Appointment Tests
    @freeze_time("2025-04-25 12:00:00")
    def test_create_new_appointment_same_day(self, client, mock_acuity):
        # Setup mock appointment data for today
        appt_id = "12345"
        appt_time = datetime(2025, 4, 25, 14, 0)  # 2pm today
        
        mock_acuity.add_appointment({
            "id": appt_id,
            "datetime": appt_time.isoformat(),
            "firstName": "John",
            "lastName": "Doe",
            "phone": "",
            "email": "",
            "date": "June 3, 2025",
            "time": "7:00pm",
            "endTime": "8:00pm",
            "dateCreated": "April 9, 2025",
            "datetimeCreated": "2025-04-09T17:15:16-0500",
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
        })

        # Simulate webhook
        response = client.post(
            "/webhook/appt-changed",
            data={
                "action": "scheduled",
                "id": appt_id,
                "calendarID": settings.calendar_id
            }
        )

        assert response.status_code == 200
        print(response.json())
        assert response.json()["status"] == "success"
        
        # Verify event creation
        event = response.json()["data"]
        assert event["action"] == EventAction.schedule
        assert event["new_time"] is not None
        assert event["old_time"] is None

    @freeze_time("2025-04-25 12:00:00")
    def test_reject_new_appointment_different_day(self, client, mock_acuity):
        # Setup mock appointment data for tomorrow
        appt_id = "new_tomorrow_1"
        tomorrow = datetime(2025, 4, 26, 14, 0)
        
        mock_acuity.add_appointment({
            "id": appt_id,
            "datetime": tomorrow.isoformat(),
            "canceled": False
        })

        response = client.post(
            "/webhook/appt-changed",
            data={
                "action": "scheduled",
                "id": appt_id,
                "calendarID": settings.calendar_id
            }
        )

        assert response.status_code == 200
        assert response.json()["status"] == "passed"
        assert "doesn't deal with today" in response.json()["message"]

    # 4. Cancellation Tests
    @freeze_time("2025-04-25 12:00:00")
    def test_cancel_existing_appointment(self, client, mock_acuity, db_session, create_test_appointment):
        # Create existing appointment in DB
        appt_id = "cancel_1"
        initial_time = datetime(2025, 4, 25, 15, 0)
        appt = create_test_appointment(
            id=appt_id,
            start_time=initial_time
        )

        # Setup mock canceled appointment
        mock_acuity.add_appointment({
            "id": appt_id,
            "datetime": initial_time.isoformat(),
            "canceled": True
        })

        response = client.post(
            "/webhook/appt-changed",
            data={
                "action": "canceled",
                "id": appt_id,
                "calendarID": settings.calendar_id
            }
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # Verify appointment state
        db_session.refresh(appt)
        assert appt.canceled == True

        # Verify event creation
        self._verify_event(
            db_session,
            appt_id,
            EventAction.cancel,
            expected_old_time=initial_time
        )

    # 5. Rescheduling Tests
    # a. Same Day Rescheduling
    @freeze_time("2025-04-25 12:00:00")
    def test_reschedule_same_day(self, client, mock_acuity, db_session, create_test_appointment):
        appt_id = "reschedule_same_day_1"
        initial_time = datetime(2025, 4, 25, 10, 0)
        new_time = datetime(2025, 4, 25, 14, 0)

        # Create initial appointment
        appt = create_test_appointment(
            id=appt_id,
            start_time=initial_time
        )

        # Setup mock rescheduled appointment
        mock_acuity.add_appointment({
            "id": appt_id,
            "datetime": new_time.isoformat(),
            "canceled": False
        })

        response = client.post(
            "/webhook/appt-changed",
            data={
                "action": "rescheduled",
                "id": appt_id,
                "calendarID": settings.calendar_id
            }
        )

        assert response.status_code == 200
        db_session.refresh(appt)
        assert appt.start_time == new_time

        self._verify_event(
            db_session,
            appt_id,
            EventAction.reschedule_same_day,
            expected_old_time=initial_time,
            expected_new_time=new_time
        )

    # b. Incoming Rescheduling
    @freeze_time("2025-04-25 12:00:00")
    def test_reschedule_incoming(self, client, mock_acuity, db_session, create_test_appointment):
        appt_id = "reschedule_incoming_1"
        initial_time = datetime(2025, 4, 26, 10, 0)  # tomorrow
        new_time = datetime(2025, 4, 25, 14, 0)  # today

        # Create initial appointment
        appt = create_test_appointment(
            id=appt_id,
            start_time=initial_time
        )

        # Setup mock rescheduled appointment
        mock_acuity.add_appointment({
            "id": appt_id,
            "datetime": new_time.isoformat(),
            "canceled": False
        })

        response = client.post(
            "/webhook/appt-changed",
            data={
                "action": "rescheduled",
                "id": appt_id,
                "calendarID": settings.calendar_id
            }
        )

        assert response.status_code == 200
        db_session.refresh(appt)
        assert appt.canceled == True

        self._verify_event(
            db_session,
            appt_id,
            EventAction.reschedule_incoming,
            expected_old_time=initial_time,
            expected_new_time=new_time
        )

    # c. Outgoing Rescheduling
    @freeze_time("2025-04-25 12:00:00")
    def test_reschedule_outgoing(self, client, mock_acuity, db_session, create_test_appointment):
        appt_id = "reschedule_outgoing_1"
        initial_time = datetime(2025, 4, 25, 10, 0)  # today
        new_time = datetime(2025, 4, 26, 14, 0)  # tomorrow

        # Create initial appointment
        appt = create_test_appointment(
            id=appt_id,
            start_time=initial_time
        )

        # Setup mock rescheduled appointment
        mock_acuity.add_appointment({
            "id": appt_id,
            "datetime": new_time.isoformat(),
            "canceled": False
        })

        response = client.post(
            "/webhook/appt-changed",
            data={
                "action": "rescheduled",
                "id": appt_id,
                "calendarID": settings.calendar_id
            }
        )

        assert response.status_code == 200
        db_session.refresh(appt)
        assert appt.start_time == new_time

        self._verify_event(
            db_session,
            appt_id,
            EventAction.reschedule_outgoing,
            expected_old_time=initial_time,
            expected_new_time=new_time
        )