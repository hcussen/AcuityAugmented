def test_protected_endpoint(test_client):
    response = test_client.get("/protected-endpoint")
    assert response.status_code == 200

def test_protected_endpoint_no_auth(test_client):
    test_client.headers = {}
    response = test_client.get("/protected-endpoint")
    assert response.status_code == 401