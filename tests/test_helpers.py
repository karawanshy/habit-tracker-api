from fastapi.testclient import TestClient
from app.crud import users
from app.schemas import UserCreate

def create_test_user(session, is_admin=False):
    user = UserCreate(
        username="admin_user" if is_admin else "regular_user",
        email="admin@example.com" if is_admin else "user@example.com",
        password="password123",
        is_admin=is_admin
    )
    return users.create_user(user, session)

def create_access_token(client: TestClient, username: str, password: str):
    response = client.post("/login", data={"username": username, "password": password})
    return response.json().get("access_token")