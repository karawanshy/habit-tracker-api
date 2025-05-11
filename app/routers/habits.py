from fastapi import APIRouter, Depends, Query
from app.database import get_db
import app.schemas as s
from app.models import Category, Frequency, User
from app.utils import normalize_category, normalize_frequency
import app.crud.habits as habits
import app.crud.completions as completions
from typing import List, Optional
from sqlmodel import Session
from app.auth import get_current_user

router = APIRouter()

# ------------------------------ POST ROUTES ------------------------------

@router.post("/", response_model=s.HabitSummary, status_code=201)
async def create_habit(
    habit: s.HabitCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Create a new habit for the authenticated user.

    Parameters:
    - habit (s.HabitCreate): Habit details to be created.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying and committing data.

    Returns:
    - s.HabitSummary: A summary of the created habit.
    """
    return habits.create_habit(habit, current_user.id, db)


@router.post("/complete/today/{habit_id}", response_model=s.HabitCompletionStatus)
async def mark_habit_completed_today(
    habit_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Mark a specific habit as completed for today.

    Parameters:
    - habit_id (int): The ID of the habit to mark as completed.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying and committing data.

    Returns:
    - s.HabitCompletionStatus: The status of the habit completion for today.
    """
    return completions.mark_habit_completed_today(habit_id, current_user.id, db)


# ------------------------------ PUT ROUTES ------------------------------

@router.put("/{habit_id}", response_model=s.HabitSummary)
async def update_habit(
    habit_id: int, 
    habit: s.HabitUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Update an existing habit's details.

    Parameters:
    - habit_id (int): The ID of the habit to update.
    - habit (s.HabitUpdate): The new habit details.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying and committing data.

    Returns:
    - s.HabitSummary: A summary of the updated habit.
    """
    return habits.update_habit(habit_id, habit, current_user.id, db)


# ------------------------------ GET ROUTES ------------------------------

@router.get("/", response_model=List[s.HabitSummary])
async def get_habits(
    category: Optional[str] = Query(default=None, description=f"One of: {', '.join(c.value for c in Category)}"),
    frequency: Optional[str] = Query(default=None, description=f"One of: {', '.join(f.value for f in Frequency)}"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of habits for the authenticated user.

    Parameters:
    - category (Optional[str]): The category to filter by.
    - frequency (Optional[str]): The frequency to filter by.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying data.

    Returns:
    - List[s.HabitSummary]: A list of habit summaries.
    """
    return habits.get_habits(db, user_id=current_user.id, category=normalize_category(category), frequency=normalize_frequency(frequency))


@router.get("/{habit_id}", response_model=s.HabitSummary)
async def get_habit_by_id(
    habit_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Retrieve a habit by its ID.

    Parameters:
    - habit_id (int): The ID of the habit to retrieve.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying data.

    Returns:
    - s.HabitSummary: A summary of the retrieved habit.
    """
    return habits.get_habit_by_id(habit_id, current_user.id, db)


@router.get("/by-name/{habit_name}", response_model=s.HabitSummary)
async def get_habit_by_name(
    habit_name: str, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Retrieve a habit by its name.

    Parameters:
    - habit_name (str): The name of the habit to retrieve.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying data.

    Returns:
    - s.HabitSummary: A summary of the retrieved habit.
    """
    return habits.get_habit_by_name(habit_name, current_user.id, db)


@router.get("/complete/{habit_id}", response_model=s.HabitWithCompletions)
async def get_habit_completion_dates(
    habit_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Retrieve the completion dates of a specific habit.

    Parameters:
    - habit_id (int): The ID of the habit to retrieve completion dates for.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying data.

    Returns:
    - s.HabitWithCompletions: A habit summary along with its completion dates.
    """
    return completions.get_habit_completion_dates(habit_id, current_user.id, db)


@router.get("/complete/today/{habit_id}", response_model=s.HabitCompletionStatus)
async def get_habit_completion_status(
    habit_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Retrieve the completion status of a specific habit for today.

    Parameters:
    - habit_id (int): The ID of the habit to check completion status for.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying data.

    Returns:
    - s.HabitCompletionStatus: The completion status of the habit for today.
    """
    return completions.get_habit_today_completion_status(habit_id, current_user.id, db)


# ------------------------------ DELETE ROUTES ------------------------------

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Delete a specific habit by its ID.

    Parameters:
    - habit_id (int): The ID of the habit to delete.
    - current_user (User): The currently authenticated user.
    - db (Session): Database session for querying and committing data.

    Returns:
    - dict: A dictionary with a success status of the deletion.
    """
    habits.delete_habit(habit_id, current_user.id, db)
    return {"success": True}
