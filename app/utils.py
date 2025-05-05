from app.models import Category, Frequency, Habit, User
from sqlmodel import Session, select
from fastapi import HTTPException, status, Query
from typing import Optional
from datetime import date

# ------------------------------ HELPER FUNCTIONS ------------------------------

def normalize_category(value: Optional[str]) -> Optional[Category]:
    """
    Normalize a string input to a valid Category enum member.
    
    Args:
        value: The category input as a string or None.
        
    Returns:
        Category: A valid Category enum member, or None if the input is None.
        
    Raises:
        HTTPException: If the input is not a valid category.
    """
    if value is None:
        return None
    if isinstance(value, Category):
        return value
    if isinstance(value, str):
        value = value.strip().lower().title()
    try:
        return Category(value)  # Try to convert the string to a Category enum
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category {value}; must be one of {[c.value for c in Category]}"
        )
    
def normalize_frequency(value: Optional[str]) -> Optional[Frequency]:
    """
    Normalize a string input to a valid Frequency enum member.
    
    Args:
        value: The frequency input as a string or None.
        
    Returns:
        Frequency: A valid Frequency enum member, or None if the input is None.
        
    Raises:
        HTTPException: If the input is not a valid frequency.
    """
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip().lower().title()
    try:
        return Frequency(value)  # Try to convert the string to a Frequency enum
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid frequency {value}; must be one of {[f.value for f in Frequency]}"
        )
    
def category_query(category: Optional[str] = Query(default=None)) -> Optional[Category]:
    """
    Query parameter function to normalize category input for filtering habits.
    
    Args:
        category: The category input as a string from the query.
        
    Returns:
        Category: The normalized Category enum value, or None if no category is provided.
    """
    return normalize_category(category)

def frequency_query(freq: Optional[str] = Query(default=None)) -> Optional[Frequency]:
    """
    Query parameter function to normalize frequency input for filtering habits.
    
    Args:
        freq: The frequency input as a string from the query.
        
    Returns:
        Frequency: The normalized Frequency enum value, or None if no frequency is provided.
    """
    return normalize_frequency(freq)
    
def normalize_name(value: str) -> str:
    """
    Normalize a habit name by converting it to title case.
    
    Args:
        value: The habit name to be normalized.
        
    Returns:
        str: The habit name in title case.
    """
    return value.strip().title()

def normalize_username(value: str) -> str:
    """
    Normalize a username by converting it to lowercase.
    
    Args:
        value: The username to be normalized.
        
    Returns:
        str: The normalized username in lowercase.
    """
    return value.strip().lower()

# ------------------------------ DATABASE FUNCTIONS ------------------------------

def get_habit_of_user(habit_id: int, user_id: int, db: Session) -> Habit:
    """
    Retrieve a Habit instance from the database by its ID for a specific user.
    
    Args:
        habit_id: The ID of the habit to retrieve.
        user_id: The ID of the user who owns the habit.
        db: The SQLAlchemy session to query the database.
        
    Returns:
        Habit: The Habit instance belonging to the user.
        
    Raises:
        HTTPException: If the habit does not exist or the user is not authorized.
    """
    db_habit = db.exec(
        select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
    ).first()

    if not db_habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habit_id} not found or not authorized."
        )
    return db_habit

def get_user(user_id: int, db: Session) -> User:
    """
    Retrieve a User instance from the database by its ID.
    
    Args:
        user_id: The ID of the user to retrieve.
        db: The SQLAlchemy session to query the database.
        
    Returns:
        User: The User instance.
        
    Raises:
        HTTPException: If the user does not exist.
    """
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    return db_user

def get_today() -> date:
    """
    Get today's date.

    Returns:
        date: The current date.
    """
    return date.today()
