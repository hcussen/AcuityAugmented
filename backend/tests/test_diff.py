import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from app.models import Appointment, Event, EventAction
import uuid
from app.config import settings

class TestScheduleDiff:
    @freeze_time("2025-04-24T09:00:00-06:00")
    def test_schedule_diff_empty(self, db_session, test_client):
        """Test that an empty schedule returns all hours with empty lists"""
        response = test_client.get('/schedule/diff')
        assert response.status_code == 200
        diffs = response.json()

        # Verify structure matches business hours
        assert len(diffs) == 4 # this date is a thursday
        for diff in diffs:
            assert "hour" in diff
            assert "added" in diff
            assert "deleted" in diff
            assert len(diff["added"]) == 0
            assert len(diff["deleted"]) == 0

    @freeze_time("2025-04-24")
    def test_schedule_new_appointment(self, db_session, test_client):
        """Test that a newly scheduled appointment appears in the correct hour's added list"""
        # Create appointment and schedule event
        appt_id = uuid.uuid4()
        appointment = Appointment(
            id=appt_id,
            acuity_id=12345,
            first_name="John",
            last_name="Doe",
            start_time=datetime.fromisoformat("2025-04-24T17:00:00-06:00"),
            acuity_created_at=datetime.now(),
            duration=60
        )
        db_session.add(appointment)
        
        event_id = uuid.uuid4()
        event = Event(
            id=event_id,
            action=EventAction.schedule,
            appointment_id=appt_id,
            new_time=datetime.fromisoformat("2025-04-24T17:00:00-06:00"),
            created_at=datetime.now()  # Explicitly set created_at to the frozen time
        )
        db_session.add(event)
        db_session.commit()

        response = test_client.get('/schedule/diff')
        assert response.status_code == 200
        diffs = response.json()
        
        # Find the 10:00 slot
        five_pm_diff = next(diff for diff in diffs if diff["hour"] == "17:00")
        print(five_pm_diff)
        assert len(five_pm_diff["added"]) == 1
        assert five_pm_diff["added"][0]["id"] == str(appt_id)
        assert five_pm_diff["added"][0]["first_name"] == "John"
        assert five_pm_diff["added"][0]["last_name"] == "Doe"
        assert len(five_pm_diff["deleted"]) == 0

    @freeze_time("2025-04-24")
    def test_schedule_cancel_appointment(self, db_session, test_client):
        """Test that a cancelled appointment appears in the correct hour's deleted list"""
        # Create appointment and cancel event
        appt_id = uuid.uuid4()
        appointment = Appointment(
            id=appt_id,
            acuity_id=12345,
            first_name="Jane",
            last_name="Smith",
            start_time=datetime.fromisoformat("2025-04-24T16:00:00-06:00"),
            acuity_created_at=datetime.fromisoformat("2025-04-23T16:00:00-06:00"),
            duration=60,
            is_canceled=True
        )
        db_session.add(appointment)
        
        event = Event(
            action=EventAction.cancel,
            appointment_id=appt_id,
            old_time=datetime.fromisoformat("2025-04-24T16:00:00-06:00"),
            created_at=datetime.now()
        )
        db_session.add(event)
        db_session.commit()

        response = test_client.get('/schedule/diff')
        assert response.status_code == 200
        diffs = response.json()
        
        # Find the 16:00 slot
        four_pm_diff = next(diff for diff in diffs if diff["hour"] == "16:00")
        assert len(four_pm_diff["deleted"]) == 1
        assert four_pm_diff["deleted"][0]["id"] == str(appt_id)
        assert four_pm_diff["deleted"][0]["first_name"] == "Jane"
        assert four_pm_diff["deleted"][0]["last_name"] == "Smith"
        assert len(four_pm_diff["added"]) == 0

    @freeze_time("2025-04-24T15:30:00-06:00")
    def test_schedule_reschedule_same_day(self, db_session, test_client):
        """Test that a same-day reschedule appears in both the old and new hour slots"""
        # Create appointment and reschedule event
        appt_id = uuid.uuid4()
        appointment = Appointment(
            id=appt_id,
            acuity_id=12345,
            first_name="Bob",
            last_name="Wilson",

            start_time=datetime.fromisoformat("2025-04-24T18:00:00-06:00"),
            acuity_created_at=datetime.fromisoformat("2025-04-23T16:00:00-06:00"),
            duration=60
        )
        db_session.add(appointment)
        
        event = Event(
            action=EventAction.reschedule_same_day,
            appointment_id=appt_id,
            old_time=datetime.fromisoformat("2025-04-24T16:00:00-06:00"),
            new_time=datetime.fromisoformat("2025-04-24T18:00:00-06:00"),
            created_at=datetime.now()
        )
        db_session.add(event)
        db_session.commit()

        response = test_client.get('/schedule/diff')
        assert response.status_code == 200
        diffs = response.json()
        
        # Find the 16:00 slot (old time)
        four_pm_diff = next(diff for diff in diffs if diff["hour"] == "16:00")
        assert len(four_pm_diff["deleted"]) == 1
        assert four_pm_diff["deleted"][0]["id"] == str(appt_id)
        assert four_pm_diff["deleted"][0]["first_name"] == "Bob"
        assert four_pm_diff["deleted"][0]["last_name"] == "Wilson"
        assert len(four_pm_diff["added"]) == 0

        # Find the 18:00 slot (new time)
        six_pm_diff = next(diff for diff in diffs if diff["hour"] == "18:00")
        assert len(six_pm_diff["added"]) == 1
        assert six_pm_diff["added"][0]["id"] == str(appt_id)
        assert six_pm_diff["added"][0]["first_name"] == "Bob"
        assert six_pm_diff["added"][0]["last_name"] == "Wilson"
        assert len(six_pm_diff["deleted"]) == 0

    @freeze_time("2025-04-24T15:30:00-06:00")
    def test_schedule_reschedule_incoming(self, db_session, test_client):
        """Test that an incoming reschedule appears only in the new hour's added list"""
        # Create appointment and reschedule event
        appt_id = uuid.uuid4()
        appointment = Appointment(
            id=appt_id,
            acuity_id=12345,
            first_name="Alice",
            last_name="Brown",
            start_time=datetime.fromisoformat("2025-04-24T19:00:00-06:00"),
            acuity_created_at=datetime.now(),
            duration=60
        )
        db_session.add(appointment)
        
        event = Event(
            action=EventAction.reschedule_incoming,
            appointment_id=appt_id,
            old_time=datetime.fromisoformat("2025-04-25T10:00:00-06:00"),  # tomorrow
            new_time=datetime.fromisoformat("2025-04-24T19:00:00-06:00"),   # today
            created_at=datetime.now()
        )
        db_session.add(event)
        db_session.commit()

        response = test_client.get('/schedule/diff')
        assert response.status_code == 200
        diffs = response.json()
        
        # Find the 19:00 slot
        seven_pm_diff = next(diff for diff in diffs if diff["hour"] == "19:00")
        assert len(seven_pm_diff["added"]) == 1
        assert seven_pm_diff["added"][0]["id"] == str(appt_id)
        assert seven_pm_diff["added"][0]["first_name"] == "Alice"
        assert seven_pm_diff["added"][0]["last_name"] == "Brown"
        assert len(seven_pm_diff["deleted"]) == 0

    @freeze_time("2025-04-24T15:30:00-06:00")
    def test_schedule_reschedule_outgoing(self, db_session, test_client):
        """Test that an outgoing reschedule appears only in the old hour's deleted list"""
        # Create appointment and reschedule event
        appt_id = uuid.uuid4()
        appointment = Appointment(
            id=appt_id,
            acuity_id=12345,
            first_name="Carol",
            last_name="Davis",
            start_time=datetime.fromisoformat("2025-04-25T10:00:00-06:00"),  # moved to tomorrow
            acuity_created_at=datetime.now(),
            duration=60
        )
        db_session.add(appointment)
        
        event = Event(
            action=EventAction.reschedule_outgoing,
            appointment_id=appt_id,
            old_time=datetime.fromisoformat("2025-04-24T19:00:00-06:00"),  # today
            new_time=datetime.fromisoformat("2025-04-25T10:00:00-06:00"),   # tomorrow
            created_at=datetime.now()
        )
        db_session.add(event)
        db_session.commit()

        response = test_client.get('/schedule/diff')
        assert response.status_code == 200
        diffs = response.json()
        
        # Find the 19:00 slot
        seven_pm_diff = next(diff for diff in diffs if diff["hour"] == "19:00")
        assert len(seven_pm_diff["deleted"]) == 1
        assert seven_pm_diff["deleted"][0]["id"] == str(appt_id)
        assert seven_pm_diff["deleted"][0]["first_name"] == "Carol"
        assert seven_pm_diff["deleted"][0]["last_name"] == "Davis"
        assert len(seven_pm_diff["added"]) == 0