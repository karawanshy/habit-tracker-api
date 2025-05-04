from app.models import Category, Frequency, Habit
from sqlmodel import Session
from fastapi import HTTPException, status, Query
from typing import Optional

# Normalize a string input to a valid Category enum member.
def normalize_category(value: Optional[str]) -> Optional[Category]:
    if value is None:
        return None
    if isinstance(value, Category):
        return value
    if isinstance(value, str):
        value = value.strip().lower().title()
    try:
        return Category(value)
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category {value}; must be one of {[c.value for c in Category]}"
        )
    
# Normalize a string input to a valid Frequency enum member.
def normalize_frequency(value: Optional[str]) -> Optional[Frequency]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip().lower().title()
    try:
        return Frequency(value)
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid frequency {value}; must be one of {[f.value for f in Frequency]}"
        )
    
def category_query(category: Optional[str] = Query(default=None)) -> Optional[Category]:
    return normalize_category(category)

def frequency_query(freq: Optional[str] = Query(default=None)) -> Optional[Frequency]:
    return normalize_frequency(freq)
    
# Normalize habit name by converting it to title case.
def normalize_name(value: str) -> str:
    return value.strip().title()

# Retrieve a Habit instance from the database by its ID.
# Raises a ValueError if the habit does not exist.
def get_habit(habit_id: int, db: Session) -> Habit:
    db_habit = db.get(Habit, habit_id)
    if not db_habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habit_id} not found."
        )
    return db_habit