"""
users.py

Handles CRUD operations related to user habits:
- Creating, updating, retrieving, and deleting habits
- Supports filtering by category and frequency
- Ensures actions are scoped to the authenticated user

Dependencies:
- FastAPI's HTTPException for error handling
- SQLModel ORM for DB interaction
"""

from sqlmodel import Session, select
import app.schemas as s
from app.models import Habit, Category, Frequency
from app.utils import get_habit_of_user, normalize_name
from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status
from app.crud.serializers import create_habit_summary


def create_habit(habit: s.HabitCreate, user_id: int, db: Session) -> s.HabitSummary:
    """
    Create a new habit for the specified user.

    Parameters:
    - habit (HabitCreate): The habit data provided by the user.
    - user_id (int): The ID of the user creating the habit.
    - db (Session): The active database session.

    Returns:
    - HabitSummary: A summary of the created habit.
    """
    db_habit = Habit(
        **habit.model_dump(exclude={"name"}),
        name=normalize_name(habit.name),  # Normalize for uniqueness and consistency
        user_id=user_id,
        start_date=date.today()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)

    return create_habit_summary(db_habit)


def update_habit(habit_id: int, habit: s.HabitUpdate, user_id: int, db: Session) -> s.HabitSummary:
    """
    Update an existing habit for a user.

    Parameters:
    - habit_id (int): The ID of the habit to update.
    - habit (HabitUpdate): The new data for the habit.
    - user_id (int): The ID of the user who owns the habit.
    - db (Session): The database session.

    Returns:
    - HabitSummary: A summary of the updated habit.
    """
    db_habit = get_habit_of_user(habit_id, user_id, db)  # Ensures user owns the habit
    
    habit_data = habit.model_dump()
    for key, value in habit_data.items():
        if value is not None:
            setattr(db_habit, key, value)  # Only update provided fields

    db.commit()
    db.refresh(db_habit)
    
    return create_habit_summary(db_habit)


def get_habits(db: Session, user_id: int, category: Optional[Category] = None, frequency: Optional[Frequency] = None) -> List[s.HabitSummary]:
    """
    Retrieve a list of all habits for a user, optionally filtered by category and frequency.

    Parameters:
    - db (Session): The database session.
    - user_id (int): The ID of the user.
    - category (Optional[Category]): Filter habits by category (optional).
    - frequency (Optional[Frequency]): Filter habits by frequency (optional).

    Returns:
    - List[HabitSummary]: A list of habit summaries.
    """
    query = select(Habit).where(Habit.user_id == user_id)

    if category:
        query = query.where(Habit.category == category)
    if frequency:
        query = query.where(Habit.frequency == frequency)

    habits = db.exec(query).all()

    return [create_habit_summary(habit) for habit in habits]


def get_habit_by_id(habit_id: int, user_id: int, db: Session) -> s.HabitSummary:
    """
    Get a single habit by its ID, ensuring the user owns it.

    Parameters:
    - habit_id (int): The ID of the habit.
    - user_id (int): The ID of the user.
    - db (Session): The database session.

    Returns:
    - HabitSummary: The summary of the retrieved habit.
    """
    db_habit = get_habit_of_user(habit_id, user_id, db)
    return create_habit_summary(db_habit)


def get_habit_by_name(name: str, user_id: int, db: Session) -> s.HabitSummary:
    """
    Retrieve a habit by its normalized name.

    Parameters:
    - name (str): The name of the habit.
    - user_id (int): The user ID (to ensure ownership).
    - db (Session): The database session.

    Returns:
    - HabitSummary: The habit summary if found.

    Raises:
    - HTTPException: If the habit is not found or not owned by the user.
    """
    name = normalize_name(name)  # Normalize to match stored format
    db_habit = db.exec(
        select(Habit)
        .where(Habit.user_id == user_id, Habit.name == name)
    ).first()

    if not db_habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with name {name} not found or not authorized."
        )
    
    return create_habit_summary(db_habit)


def delete_habit(habit_id: int, user_id: int, db: Session) -> bool:
    """
    Delete a habit owned by the user.

    Parameters:
    - habit_id (int): The ID of the habit to delete.
    - user_id (int): The user ID.
    - db (Session): The database session.

    Returns:
    - bool: True if deletion succeeded.
    """
    db_habit = get_habit_of_user(habit_id, user_id, db)
    db.delete(db_habit)
    db.commit()
    return True
