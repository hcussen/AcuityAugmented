import pytest
from freezegun import freeze_time
from datetime import datetime, timedelta
from app.config import settings
from app.models import Event, EventAction, Appointment
from app.core.time_utils import isToday
import json
from sqlalchemy import select
import uuid

class TestIsToday:
    @freeze_time("2025-04-25")
    def test_is_today(self):
        assert isToday("2025-04-25T19:00:00-0600")

@pytest.fixture(scope="class")
def appointment_details():
    return {
        "id": 12345,
        "firstName": "Meredith",
        "lastName": "Gray",
        "phone": "",
        "email": "",
        "date": "April 25, 2025",
        "time": "7:00pm",
        "endTime": "8:00pm",
        "dateCreated": "April 24, 2025",
        "datetimeCreated": "2025-04-24T19:00:00-0600",
        "datetime": "2025-04-25T19:00:00-0600",
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
        "calendar": "Gray Sloan General Surgery",
        "calendarID": settings.calendar_id,
        "certificate": None,
        "confirmationPage": "scheudling.graysloanmemorial.com",
        "confirmationPagePaymentLink": "scheudling.graysloanmemorial.com",
        "location": "Gray Sloan Memorial Hospital",
        "notes": "",
        "timezone": "America/Seattle",
        "calendarTimezone": "America/Seattle",
        "canceled": False,
        "canClientCancel": True,
        "canClientReschedule": True,
        "labels": None,
        "forms": [],
        "formsText": "a form",
        "isVerified": False,
        "scheduledBy": "example@graysloanmemorial.com"
    }


class TestWebhooks:

    def test_not_from_calendar_of_interest(self, db_session, test_client, patched_acuity_client):
        response = test_client.post('/webhook/appt-changed',
                         data={
                             'action': 'changed',
                             'id': '123456',
                             'calendarID': '12345',
                             'type': '77085032'
                         })
        assert response.status_code == 200
        content = response.json()
        assert content['status'] == 'passed'
    
    @freeze_time("2025-04-20")
    def test_newly_scheduled_not_today(self, db_session, test_client, patched_acuity_client, appointment_details):
        # precondition: there is no existing appt in the db 
        assert datetime.now().date() == datetime.fromisoformat("2025-04-20").date()
        
        appointment_details = {
            "id": 12345,
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "date": "June 3, 2025",
            "time": "7:00pm", 
            "endTime": "8:00pm",
            "datetime": "2025-06-03T19:00:00-0600",
            "type": "Math Tutoring",
            "duration": "60"
        }
    

        # Add the appointment to the mock client
        patched_acuity_client.add_appointment(appointment_details)

        response = test_client.post('/webhook/appt-changed',
                            data={
                                'action': 'changed',
                                'id': '12345',
                                'calendarID': settings.calendar_id,
                                'type': '77085032'
                            })

        print(response.json())
        assert response.status_code == 200
        content = response.json()
        assert content['status'] == 'passed'
        assert content['message'] == f"Appt 12345 doesn't deal with today"

    @freeze_time("2025-04-25")
    def test_newly_scheduled_is_today(self, db_session, test_client, patched_acuity_client, appointment_details):
        # precondition: there is no existing appt in the db 
        
        # Add the appointment to the mock client
        patched_acuity_client.add_appointment(appointment_details)

        response = test_client.post('/webhook/appt-changed',
                         data={
                             'action': 'changed',
                             'id': '12345',
                             'calendarID': settings.calendar_id,
                             'type': '77085032'
                         })
        
        event = Event(
                action=EventAction.schedule,
                old_time=None,
                new_time="2025-04-25T19:00:00-0600",
                appointment_id=12345
            )

        content = response.json()
        returnedEvent = json.loads(content['data'])
        print(content)
        assert response.status_code == 200
        assert content['status'] == 'success'
        assert returnedEvent['action'] == event.action.value
        assert returnedEvent['old_time'] == event.old_time

        # Parse both strings to datetime objects
        returned_dt = datetime.strptime(returnedEvent['new_time'], '%Y-%m-%d %H:%M:%S')
        event_dt = datetime.fromisoformat(event.new_time.replace('Z', '+00:00')).replace(tzinfo=None)

        # Then compare the datetime objects
        assert returned_dt == event_dt

        # assert the appointment was created
        q = select(Appointment).where(Appointment.id == uuid.UUID(returnedEvent['appointment_id']))
        existing_appt = db_session.scalars(q).all()[0]
        assert existing_appt

    @freeze_time("2025-04-25")
    def test_cancel_appointment(self, db_session, test_client, patched_acuity_client, appointment_details):
        # Create an existing appointment in the database
        id = uuid.uuid4()
        acuity_id = 12345
        appt = Appointment(
            id=id,
            acuity_id=acuity_id,
            first_name="John",
            last_name="Doe",
            start_time=datetime.fromisoformat("2025-04-25T19:00:00-0600"),
            acuity_created_at=datetime.now() - timedelta(days=1),
            duration=60,
            is_canceled=False
        )
        db_session.add(appt)
        db_session.commit()

        # assert the appointment was created
        q = select(Appointment).where(Appointment.id == id)
        existing_appt = db_session.scalars(q).all()[0]
        assert existing_appt

        # Setup mock appointment response with canceled=True
        appointment_details['canceled'] = True
        patched_acuity_client.add_appointment(appointment_details)

        response = test_client.post('/webhook/appt-changed',
                         data={
                             'action': 'canceled',
                             'id': str(acuity_id),
                             'calendarID': settings.calendar_id
                         })
        
        # assert the appointment was created
        q = select(Appointment).where(Appointment.id == id)
        fresh_appt = db_session.scalars(q).all()[0]
        assert fresh_appt

        content = response.json()
        assert response.status_code == 200
        assert content['status'] == 'success'

        # Verify event creation
        event_data = json.loads(content['data'])
        assert event_data['action'] == EventAction.cancel.value
        assert datetime.strptime(event_data['old_time'], '%Y-%m-%d %H:%M:%S') == fresh_appt.start_time.replace(tzinfo=None)
        assert event_data['new_time'] is None

        # Verify appointment state in database
        assert fresh_appt.is_canceled == True

    @freeze_time("2025-04-25")
    def test_reschedule_same_day(self, db_session, test_client, patched_acuity_client):
        # Create an existing appointment
        id = uuid.uuid4()
        acuity_id = 12345
        old_start_time = "2025-04-25T14:00:00-0600"
        appt = Appointment(
            id=id,
            acuity_id=acuity_id,
            first_name="John",
            last_name="Doe",
            start_time=datetime.fromisoformat(old_start_time),
            acuity_created_at=datetime.now() - timedelta(days=1),
            duration=60,
            is_canceled=False
        )
        db_session.add(appt)
        db_session.commit()

        # Setup mock appointment with new time
        appointment_details = {
            "id": 12345,
            "firstName": "John",
            "lastName": "Doe",
            "datetime": "2025-04-25T16:00:00-0600",
            "duration": "60",
            "canceled": False
        }
        patched_acuity_client.add_appointment(appointment_details)

        response = test_client.post('/webhook/appt-changed',
                         data={
                             'action': 'rescheduled',
                             'id': str(acuity_id),
                             'calendarID': settings.calendar_id
                         })
        
        # assert the appointment was created
        q = select(Appointment).where(Appointment.id == id)
        fresh_appt = db_session.scalars(q).all()[0]
        assert fresh_appt
        
        content = response.json()
        assert response.status_code == 200
        assert content['status'] == 'success'

        # Verify event creation
        event_data = json.loads(content['data'])
        assert event_data['action'] == EventAction.reschedule_same_day.value
        assert datetime.strptime(event_data['old_time'], '%Y-%m-%d %H:%M:%S') == datetime.fromisoformat(old_start_time).replace(tzinfo=None)
        assert datetime.strptime(event_data['new_time'], '%Y-%m-%d %H:%M:%S') == datetime.fromisoformat("2025-04-25T16:00:00-0600").replace(tzinfo=None)

        # Verify appointment update in database
        q = select(Appointment).where(Appointment.id == id)
        updated_appt = db_session.scalars(q).first()
        expected_time = datetime.fromisoformat("2025-04-25T16:00:00-0600").replace(tzinfo=None)
        assert updated_appt.start_time == expected_time

    @freeze_time("2025-04-25")
    def test_reschedule_incoming(self, db_session, test_client, patched_acuity_client):
        # Create an existing appointment for a different day
        id = uuid.uuid4()
        acuity_id = 12345
        appt = Appointment(
            id=id,
            acuity_id=acuity_id,
            first_name="John",
            last_name="Doe",
            start_time=datetime.fromisoformat("2025-04-26T14:00:00-0600"),
            acuity_created_at=datetime.now() - timedelta(days=1),
            duration=60,
            is_canceled=False
        )
        db_session.add(appt)
        db_session.commit()

        # Setup mock appointment rescheduled to today
        appointment_details = {
            "id": 12345,
            "firstName": "John",
            "lastName": "Doe",
            "datetime": "2025-04-25T16:00:00-0600",
            "duration": "60",
            "canceled": False
        }
        patched_acuity_client.add_appointment(appointment_details)

        response = test_client.post('/webhook/appt-changed',
                         data={
                             'action': 'rescheduled',
                             'id': '12345',
                             'calendarID': settings.calendar_id
                         })
        
        content = response.json()
        assert response.status_code == 200
        assert content['status'] == 'success'

        # Verify appointment is marked as canceled
        q = select(Appointment).where(Appointment.id == id)
        updated_appt = db_session.scalars(q).first()
        assert updated_appt.is_canceled == True

        # Verify event creation
        event_data = json.loads(content['data'])
        assert event_data['action'] == EventAction.reschedule_incoming.value
        assert datetime.strptime(event_data['old_time'], '%Y-%m-%d %H:%M:%S') == updated_appt.start_time.replace(tzinfo=None)
        assert datetime.strptime(event_data['new_time'], '%Y-%m-%d %H:%M:%S') == datetime.fromisoformat("2025-04-25T16:00:00-0600").replace(tzinfo=None)

        

    @freeze_time("2025-04-25")
    def test_reschedule_outgoing(self, db_session, test_client, patched_acuity_client):
        # Create an existing appointment for today
        id = uuid.uuid4()
        acuity_id = 12345
        appt = Appointment(
            id=id,
            acuity_id=acuity_id,
            first_name="John",
            last_name="Doe",
            start_time=datetime.fromisoformat("2025-04-25T14:00:00-0600"),
            acuity_created_at=datetime.now() - timedelta(days=1),
            duration=60,
            is_canceled=False
        )
        db_session.add(appt)
        db_session.commit()

        # Setup mock appointment rescheduled to a different day
        appointment_details = {
            "id": 12345,
            "firstName": "John",
            "lastName": "Doe",
            "datetime": "2025-04-26T16:00:00-0600",
            "duration": "60",
            "canceled": False
        }
        patched_acuity_client.add_appointment(appointment_details)

        response = test_client.post('/webhook/appt-changed',
                         data={
                             'action': 'rescheduled',
                             'id': '12345',
                             'calendarID': settings.calendar_id
                         })
        
        content = response.json()
        assert response.status_code == 200
        assert content['status'] == 'success'

        # Verify appointment time update
        q = select(Appointment).where(Appointment.id == id)
        updated_appt = db_session.scalars(q).first()
        assert updated_appt.start_time == datetime.fromisoformat("2025-04-26T16:00:00-0600").replace(tzinfo=None)   

        # Verify event creation
        event_data = json.loads(content['data'])
        assert event_data['action'] == EventAction.reschedule_outgoing.value
        assert datetime.strptime(event_data['old_time'], '%Y-%m-%d %H:%M:%S') == datetime.fromisoformat("2025-04-25T14:00:00-0600").replace(tzinfo=None)
        assert datetime.strptime(event_data['new_time'], '%Y-%m-%d %H:%M:%S') == datetime.fromisoformat("2025-04-26T16:00:00-0600").replace(tzinfo=None)

       