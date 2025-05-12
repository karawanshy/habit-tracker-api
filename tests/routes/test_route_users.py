from app import models
from app.crud import users
from fastapi.testclient import TestClient

def test_admin_can_get_users(client: TestClient, session, admin_user_token):
    """
    Test that an admin user can retrieve a list of all users.
    """
    headers = {"Authorization": f"Bearer {admin_user_token}"}
    response = client.get("/users/", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["username"] == "admin_user"

def test_regular_user_cannot_get_users(client: TestClient, session, regular_user_token):
    """
    Test that a regular user cannot retrieve the list of all users.
    """
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    response = client.get("/users/", headers=headers)
    
    # Assuming a regular user should not have access and receives a 403 Forbidden
    assert response.status_code == 403