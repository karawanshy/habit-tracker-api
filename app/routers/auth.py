"""
auth.py

Provides authentication routes including user login and protected endpoints.
Implements OAuth2 password flow and JWT-based access tokens.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
import app.schemas as s
from app.models import User
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth import authenticate_user, create_access_token, get_current_user

# Create a FastAPI router instance for auth-related endpoints
router = APIRouter()


@router.post("/login", response_model=s.UserLoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.

    This endpoint uses OAuth2 with password flow to validate the user credentials
    and returns a JWT token for future authenticated requests.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): Login form data (username & password).
    - db (Session): SQLAlchemy database session.

    Returns:
    - UserLoginResponse: Contains username, access token, and token type.

    Raises:
    - HTTPException: If authentication fails.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate user.")

    # Generate a JWT token valid for 20 minutes
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return s.UserLoginResponse(
        username=user.username,
        access_token=token,
        token_type="bearer"
    )


@router.get("/secure-data")
async def secure_endpoint(current_user: User = Depends(get_current_user)):
    """
    A protected route that requires user authentication.

    Parameters:
    - current_user (User): Automatically injected from the JWT via dependency.

    Returns:
    - dict: A simple message with the authenticated user's username.
    """
    return {
        "msg": f"You're authenticated as {current_user.username}!"
    }
