from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

from urllib.parse import unquote

print(f"Raw DATABASE_URL from environment: {os.getenv('DATABASE_URL')}")
print(f"Decoded DATABASE_URL: {unquote(os.getenv('DATABASE_URL'))}")

# Raise an error if the DATABASE_URL is not found in the .env file
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not found in .env file")

# Create the database engine using the DATABASE_URL
# 'echo=True' enables SQLAlchemy logging for SQL queries executed
engine = create_engine(DATABASE_URL, echo=True)

# ---------------------------- Database Initialization ----------------------------

def init_db():
    """
    Initialize the database by creating all tables defined in SQLModel models.

    It should be called once at the start of the application to ensure the 
    database schema is up-to-date.
    """
    SQLModel.metadata.create_all(engine)

# ---------------------------- Session Management ----------------------------

def get_db():
    """
    Provides a database session to interact with the database.

    This function uses dependency injection in FastAPI to provide a session
    that allows for safe and efficient queries to the database.

    It ensures that the session is closed after usage to release database resources.

    Yields:
    - Session: A SQLAlchemy Session object used to interact with the database.
    """
    with Session(engine) as db:
        try:
            yield db  # Yield the session to be used by FastAPI endpoints
        finally:
            db.close()  # Ensure the session is closed after usage
