import pytest
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine, StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from tests.test_helpers import create_access_token
from app import models
from uuid import uuid4
from app.schemas import UserCreate

# Use in-memory SQLite for testing
DATABASE_URL = "sqlite:///:memory:"

# Create the test engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Pytest fixture for DB session
@pytest.fixture
def session() -> Generator[Session, None, None]:
    """
    Fixture to provide a database session for testing.

    This fixture creates a new session for each test, ensuring that the tests
    are isolated and do not affect each other. It also handles the teardown
    by closing the session after the test is done.
    """
    # drop & create the database tables before each test for isolation
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    
    # Create a new session
    db = Session(bind=engine)
    
    try:
        yield db  # Provide the session to the test
    finally:
        db.close()

@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture to provide a TestClient for testing FastAPI endpoints.

    This fixture uses the session fixture to ensure that each test has a
    clean database state. It also overrides the get_db dependency to use
    the test session.
    """
    # Override the get_db dependency to use the test session
    def override_get_db():
        yield session

    # Inject the overrided dependency into the app
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear() # Clear the overrides after the test

@pytest.fixture
def user_factory(client: TestClient, session: Session):
    def _create_user(is_admin=False):
        user_data = {
            "username": f"admin_user {uuid4()}" if is_admin else f"regular_user {uuid4()}",
            "email": "admin@example.com" if is_admin else "user@example.com",
            "password": "password123",
            "is_admin": is_admin
        }   
        
        response = client.post(
            "/users/",
            json=user_data
        )

        assert response.status_code == 201
        return response.json()
    return _create_user

@pytest.fixture
def admin_user_token(client: TestClient, user_factory) -> str:
    user = user_factory(is_admin=True)
    return create_access_token(client, user['username'], 'password123')

@pytest.fixture
def regular_user_token(client: TestClient, user_factory) -> str:
    user = user_factory(is_admin=False)
    return create_access_token(client, user['username'], 'password123')

@pytest.fixture
def create_test_habit(client: TestClient, regular_user_token):
    name = f"read books {uuid4()}"  # avoid name collision
    
    habit_data = {
        "name": name,
        "description": "Read 30 minutes daily",
        "category": "personal development",
        "frequency": "daily"
    }

    response = client.post(
        "/habits/",
        json=habit_data,
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == 201
    return response.json()
