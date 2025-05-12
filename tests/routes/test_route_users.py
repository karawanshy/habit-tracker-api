from app import models
from app.crud import users
from fastapi.testclient import TestClient
from tests.test_helpers import create_access_token

def test_create_user(client: TestClient, user_factory):
    user = user_factory()
    assert user["username"].startswith("regular_user")
    assert user["email"] == "user@example.com"
    assert "id" in user

def test_create_user_with_invalid_email(client: TestClient, user_factory):
    user_data = {
        "username": "regular_user",
        "email": "invalid-email",  # Invalid email
        "password": "password123"
    }
    
    response = client.post("/users/", json=user_data)

    # Assert that the status code is 422, indicating a validation error
    assert response.status_code == 422
    assert response.json()['detail'][0]['input'] == 'invalid-email'

def test_update_user(client: TestClient, user_factory, regular_user_token):
    updated_user_data = {"username": "updated_username"}

    response = client.put(
        f"/users/me/",
        json=updated_user_data,
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == "updated_username"
  
def test_admin_can_get_users(client: TestClient, admin_user_token):
    """
    Test that an admin user can retrieve a list of all users.
    """
    headers = {"Authorization": f"Bearer {admin_user_token}"}
    response = client.get("/users/", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["username"].startswith("admin_user")

def test_regular_user_cannot_get_users(client: TestClient, regular_user_token):
    """
    Test that a regular user cannot retrieve the list of all users.
    """
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    response = client.get("/users/", headers=headers)
    
    # Assuming a regular user should not have access and receives a 403 Forbidden
    assert response.status_code == 403

def test_get_user_by_id(client: TestClient, user_factory, admin_user_token):
    user = user_factory()

    response = client.get(
        f"/users/{user['id']}",
        headers={"Authorization": f"Bearer {admin_user_token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == user['id']
    assert response.json()["username"] == user['username']

def test_get_user_by_id_not_found(client: TestClient, admin_user_token):
    non_existent_user_id = 99999  # Assuming this ID does not exist
    
    response = client.get(
        f"/users/{non_existent_user_id}",
        headers={"Authorization": f"Bearer {admin_user_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_regular_user_cannot_get_other_users(client: TestClient, user_factory, regular_user_token):
    other_user = user_factory()

    response = client.get(
        f"/users/{other_user['id']}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 403
    assert "admin access required" in response.json()["detail"].lower()

def test_get_user_by_username(client: TestClient, user_factory, admin_user_token):
    user = user_factory()

    response = client.get(
        f"/users/by-username/{user['username']}",
        headers={"Authorization": f"Bearer {admin_user_token}"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == user["username"]
    assert response.json()["id"] == user["id"]

def test_get_user_by_username_not_found(client: TestClient, admin_user_token):
    non_existent_username = "nonexistentuser123"

    response = client.get(
        f"/users/by-username/{non_existent_username}",
        headers={"Authorization": f"Bearer {admin_user_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_regular_user_cannot_get_user_by_username(client: TestClient, user_factory, regular_user_token):
    other_user = user_factory()

    response = client.get(
        f"/users/by-username/{other_user['username']}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 403
    assert "admin access required" in response.json()["detail"].lower()

def test_user_can_delete_own_account(client: TestClient, user_factory):
    user = user_factory()
    token = create_access_token(client, user['username'], 'password123')

    response = client.delete(
        f"/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
