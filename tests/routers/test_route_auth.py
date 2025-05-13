from tests.conftest import create_access_token

def test_login_valid_credentials(client, user_factory):
    user = user_factory()
    response = client.post("/login", data={"username": user["username"], "password": "password123"})

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    response = client.post("/login", data={"username": "wronguser", "password": "wrongpass"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_secure_endpoint_valid_token(client, user_factory):
    user = user_factory()
    token = create_access_token(client, user["username"], "password123")

    response = client.get("/secure-data", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert "You're authenticated" in response.json()["msg"]

def test_secure_endpoint_invalid_token(client):
    response = client.get("/secure-data", headers={"Authorization": "Bearer invalidtoken123"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"