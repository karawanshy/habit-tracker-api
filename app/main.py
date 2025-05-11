from fastapi import FastAPI, Depends
from app.database import init_db
from app.routers import users, habits, auth
from contextlib import asynccontextmanager
from app.auth import get_current_user
from app.models import User
from app.schemas import UserResponse

# -------------------------- Lifespan Management --------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager to handle the app's lifespan events, such as 
    initialization and shutdown procedures.

    This context manager is used to initialize the database connection when the
    application starts and prints a message. It also manages the shutdown by 
    printing a message when the application shuts down.

    Args:
    - app (FastAPI): The FastAPI application instance.
    """
    # Initialize the database on startup
    init_db()
    print("Database initialized.")
    
    # Yield control back to FastAPI to run the application
    yield
    
    print("Shutting down Habit Tracker API.")

# -------------------------- FastAPI App Setup --------------------------

# Create FastAPI application instance with a lifespan context
app = FastAPI(
    title="Habit Tracker API",
    lifespan=lifespan
)

# -------------------------- Routers Setup --------------------------

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(auth.router, tags=["Auth"])

# -------------------------- Root Endpoint --------------------------

@app.get("/", response_model=UserResponse)
async def root(current_user: User = Depends(get_current_user)):
    """
    Root endpoint that returns the current authenticated user's data.

    This endpoint fetches the authenticated user based on the provided JWT token
    using the get_current_user dependency. It returns the user details in a 
    response formatted according to the UserResponse schema.

    Args:
    - current_user (User): The currently authenticated user.

    Returns:
    - UserResponse: The current user's data in the response model.
    """
    return current_user
