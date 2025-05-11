"""
users.py

Handles CRUD operations for User entities, including account creation, updating details, 
fetching user data, and deletion. Ensures usernames are normalized and password handling is secure.
"""

from sqlmodel import Session, select
import app.schemas as s
from app.models import User
from app.utils import normalize_username, get_user
from typing import List
from fastapi import HTTPException, status
from app.crud.serializers import create_user_summary


def create_user(user: s.UserCreate, db: Session) -> s.UserSummary:
    """
    Create a new user in the database.

    Parameters:
    - user (UserCreate): User registration details.
    - db (Session): Database session.

    Returns:
    - UserSummary: A simplified response model of the newly created user.
    """
    db_user = User(
        username=normalize_username(user.username),  # Ensure consistent formatting
        email=user.email,
        is_admin=user.is_admin
    )
    db_user.set_password(user.password)  # Hash and store the password securely

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return s.UserSummary(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
    )


def update_user(user: s.UserUpdate, user_id: int, db: Session) -> s.UserSummary:
    """
    Update user information.

    Parameters:
    - user (UserUpdate): Fields to update.
    - user_id (int): ID of the user to update.
    - db (Session): Database session.

    Returns:
    - UserSummary: Updated user summary.
    """
    db_user = get_user(user_id, db)

    # Update only fields that are provided
    if user.username:
        db_user.username = user.username
    if user.password:
        db_user.set_password(user.password)
    if user.email:
        db_user.email = user.email

    db.commit()
    db.refresh(db_user)

    return create_user_summary(db_user)


def get_users(db: Session) -> List[s.UserSummary]:
    """
    Fetch all users from the database.

    Parameters:
    - db (Session): Database session.

    Returns:
    - List[UserSummary]: List of all user summaries.
    """
    db_users = db.exec(select(User)).all()
    return [create_user_summary(user) for user in db_users]


def get_user_by_id(user_id: int, db: Session) -> s.UserSummary:
    """
    Fetch a single user by ID.

    Parameters:
    - user_id (int): User's ID.
    - db (Session): Database session.

    Returns:
    - UserSummary: Summary of the user.
    """
    db_user = get_user(user_id, db)
    return create_user_summary(db_user)


def get_user_by_username(username: str, db: Session) -> s.UserSummary:
    """
    Fetch a user by username.

    Parameters:
    - username (str): The user's username.
    - db (Session): Database session.

    Returns:
    - UserSummary: Summary of the found user.

    Raises:
    - HTTPException: If user is not found.
    """
    username = normalize_username(username)
    db_user = db.exec(
        select(User).where(User.username == username)
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found."
        )

    return create_user_summary(db_user)


def delete_user(user_id: int, db: Session) -> bool:
    """
    Delete a user by ID.

    Parameters:
    - user_id (int): ID of the user to delete.
    - db (Session): Database session.

    Returns:
    - bool: True if deletion was successful.
    """
    db_user = get_user(user_id, db)
    db.delete(db_user)
    db.commit()
    return True
