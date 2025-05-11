from app import models
from app.crud import users
from fastapi.testclient import TestClient
import pytest
from app.tests.test_helpers import create_test_user, get_auth_headers

@pytest.fixture
def admin_user(session):
    return create_test_user(session, is_admin=True)

@pytest.fixture
def regular_user(session):
    return create_test_user(session, is_admin=False)

def test_admin_can_get_users(client: TestClient, session, admin_user):
    """
    Test that an admin user can retrieve a list of all users.
    """
    headers = get_auth_headers(client, "admin_user", "password123")
    response = client.get("/users/", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["username"] == "admin_user"

def test_regular_user_cannot_get_users(client: TestClient, session, regular_user):
    """
    Test that a regular user cannot retrieve the list of all users.
    """
    headers = get_auth_headers(client, "regular_user", "password123")
    response = client.get("/users/", headers=headers)
    
    # Assuming a regular user should not have access and receives a 403 Forbidden
    assert response.status_code == 403