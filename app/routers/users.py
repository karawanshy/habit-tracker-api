from fastapi import APIRouter, Depends
from app.database import get_db
import app.schemas as s
from app.models import User
import app.crud.users as users
from typing import List
from sqlmodel import Session
from app.auth import get_current_user, require_admin

router = APIRouter()

# ------------------------------ POST ROUTES ------------------------------

@router.post("/", response_model=s.UserSummary, status_code=201)
async def create_user(
    user: s.UserCreate,  # User details to create a new user.
    db: Session = Depends(get_db)  # Dependency to get the database session.
):
    """
    Create a new user in the database.

    Parameters:
    - user (s.UserCreate): User details to be created.
    - db (Session): Database session for querying and committing data.

    Returns:
    - s.UserSummary: A summary of the created user's details (ID, username, etc.)
    """
    return users.create_user(user, db)


# ------------------------------ PUT ROUTES ------------------------------

@router.put("/me", response_model=s.UserSummary)
async def update_user(
    user: s.UserUpdate,  # Updated user details.
    current_user: User = Depends(get_current_user),  # Dependency to get the currently authenticated user.
    db: Session = Depends(get_db)  # Dependency to get the database session.
):
    """
    Update the details of the authenticated user.

    Parameters:
    - user (s.UserUpdate): The new user details to update.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying and committing data.

    Returns:
    - s.UserSummary: A summary of the updated user details.
    """
    return users.update_user(user, current_user.id, db)


# ------------------------------ GET ROUTES ------------------------------

@router.get("/", response_model=List[s.UserSummary], dependencies=[Depends(require_admin)])
async def get_users(
    db: Session = Depends(get_db)  # Dependency to get the database session.
):
    """
    Retrieve a list of all users.

    Parameters:
    - db (Session): Database session for querying data.

    Returns:
    - List[s.UserSummary]: A list of user summaries, each containing user details.
    """
    return users.get_users(db)

@router.get("/{user_id}", response_model=s.UserSummary, dependencies=[Depends(require_admin)])
async def get_user_by_id(
    user_id: int,  # ID of the user to retrieve.
    db: Session = Depends(get_db)  # Dependency to get the database session.
):
    """
    Retrieve a specific user by their ID.

    Parameters:
    - user_id (int): The ID of the user to retrieve.
    - db (Session): Database session for querying data.

    Returns:
    - s.UserSummary: A summary of the retrieved user's details.
    """
    return users.get_user_by_id(user_id, db)


@router.get("/by-username/{username}", response_model=s.UserSummary, dependencies=[Depends(require_admin)])
async def get_user_by_username(
    username: str,  # Username of the user to retrieve.
    db: Session = Depends(get_db)  # Dependency to get the database session.
):
    """
    Retrieve a specific user by their username.

    Parameters:
    - username (str): The username of the user to retrieve.
    - db (Session): Database session for querying data.

    Returns:
    - s.UserSummary: A summary of the retrieved user's details.
    """
    return users.get_user_by_username(username, db)


# ------------------------------ DELETE ROUTES ------------------------------

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,  # ID of the user to delete.
    current_user: User = Depends(get_current_user),  # Dependency to get the currently authenticated user.
    db: Session = Depends(get_db)  # Dependency to get the database session.
):
    """
    Delete a specific user by their ID. Only the authenticated user can delete their own account.

    Parameters:
    - user_id (int): The ID of the user to delete.
    - current_user (User): The currently authenticated user who must match the user to be deleted.
    - db (Session): Database session for querying and committing data.

    Returns:
    - dict: A dictionary indicating the success of the deletion.
    """
    users.delete_user(user_id, current_user.id, db)
    return {"success": True}
