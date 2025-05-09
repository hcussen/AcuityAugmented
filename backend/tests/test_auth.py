def test_protected_endpoint(test_client):
    response = test_client.get("/protected-endpoint")
    assert response.status_code == 200