
def test_fetch_appointment(test_client, patched_acuity_client):
    # Add a test appointment to the mock
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
    
    # Make the HTTP request through the test client
    response = test_client.get(f"/acuity/appointment?id=12345")
    assert response.status_code == 200
    
    # Get the response data
    fetched_appointment = response.json()
    
    # Assert the expected results
    assert fetched_appointment["id"] == appointment_details["id"]
    assert fetched_appointment["firstName"] == "John"
    assert fetched_appointment["lastName"] == "Doe"
    assert fetched_appointment["type"] == "Math Tutoring"