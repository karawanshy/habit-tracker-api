from fastapi.testclient import TestClient
from app.crud import users
from app.schemas import UserCreate
from uuid import uuid4

def create_access_token(client: TestClient, username: str, password: str):
    response = client.post("/login", data={"username": username, "password": password})
    token = response.json().get("access_token")
    assert token is not None, f"Failed to get access token for {username}"
    return token