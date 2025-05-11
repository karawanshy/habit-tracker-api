import pytest
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine, StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app import models

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