"""
serializers.py

Responsible for converting ORM models into API-friendly response schemas.
This module keeps the API responses decoupled from the database structure.

Functions:
- create_habit_summary: Converts a Habit ORM object to a HabitSummary schema.
- create_user_summary: Converts a User ORM object to a UserSummary schema with basic habit info.
"""

import app.schemas as s
from app.models import User, Habit


def create_habit_summary(habit: Habit) -> s.HabitSummary:
    """
    Convert a Habit ORM object to a HabitSummary Pydantic schema.

    Parameters:
    - habit (Habit): The ORM object from the database.

    Returns:
    - HabitSummary: A serialized version of the habit for API response.
    """
    return s.HabitSummary(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        category=habit.category,
        frequency=habit.frequency,
        reminder_time=habit.reminder_time,
        start_date=habit.start_date,
    )


def create_user_summary(user: User) -> s.UserSummary:
    """
    Convert a User ORM object to a UserSummary Pydantic schema.

    This includes a list of the user's habits with only basic info (ID and name).

    Parameters:
    - user (User): The ORM user instance from the DB.

    Returns:
    - UserSummary: A summarized user profile with basic habit info.
    """
    return s.UserSummary(
        id=user.id,
        username=user.username,
        email=user.email,
        habits=[
            s.HabitBasicInfo(id=habit.id, name=habit.name)
            for habit in user.habits
        ] if user.habits else []
    )
