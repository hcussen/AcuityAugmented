from freezegun import freeze_time
from datetime import datetime
from app.config import settings

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
    def test_newly_scheduled_not_today(self, db_session, test_client, patched_acuity_client):
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

    # @freeze_time("2025-04-25")
    # def test_newly_scheduled_is_today(self, db_session, test_client, patched_acuity_client):
    #     # precondition: there is no existing appt in the db 

    #     appointment_details = {
    #         "id": 12345,
    #         "firstName": "John",
    #         "lastName": "Doe",
    #         "datetime": "2025-04-25T19:00:00-0600",
    #         "duration": "60"
    #     }
    
    #     # Add the appointment to the mock client
    #     patched_acuity_client.add_appointment(appointment_details)

    #     response = test_client.post('/webhook/appt-changed',
    #                      data={
    #                          'action': 'changed',
    #                          'id': '12345',
    #                          'calendarID': '12345',
    #                          'type': '77085032'
    #                      })

    #     assert response.status_code == 200
    #     content = response.json()
    #     assert content['status'] == 'passed'
        
    