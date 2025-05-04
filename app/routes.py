from fastapi import APIRouter, Depends, Query
from app.database import get_session
import app.schemas as s
from app.models import Category, Frequency
from app.utils import normalize_name, normalize_category, normalize_frequency
import app.crud as crud
from typing import List, Optional
from sqlmodel import Session

router = APIRouter()

# ------------------------------ POST ROUTES ------------------------------

@router.post("/habits/", response_model=s.HabitSummary)
async def create_habit(habit: s.HabitCreate, db: Session = Depends(get_session)):
    return crud.create_habit(habit, db)

@router.post("/habits/{habit_id}", response_model=s.HabitSummary)
async def update_habit(habit_id: int, habit: s.HabitUpdate, db: Session = Depends(get_session)):
    return crud.update_habit(habit_id, habit, db)

@router.post("/habits/complete/today/{habit_id}", response_model=s.HabitCompletionStatus)
async def mark_habit_completed_today(habit_id: int, status: bool, db: Session = Depends(get_session)):
    return crud.mark_habit_completed_today(habit_id, status, db)

@router.post("/users/", response_model=s.UserSummary)
async def create_user(user: s.UserCreate, db: Session = Depends(get_session)):
    return crud.create_user(user, db)

@router.post("/users/{user_id}", response_model=s.UserSummary)
async def update_user(user_id: int, user: s.UserUpdate, db: Session = Depends(get_session)):
    return crud.update_user(user_id, user, db)

# ------------------------------ GET ROUTES ------------------------------

@router.get("/habits/", response_model=List[s.HabitSummary])
def get_habits(
    category: Optional[str] = Query(default=None, description=f"One of: {', '.join(c.value for c in Category)}"),
    frequency: Optional[str] = Query(default=None, description=f"One of: {', '.join(f.value for f in Frequency)}"),

    db: Session = Depends(get_session)
):
    return crud.get_habits(db,
                           category=normalize_category(category),
                           frequency=normalize_frequency(frequency))

@router.get("/habits/{habit_id}", response_model=s.HabitSummary)
async def get_habit_by_id(habit_id: int, db: Session = Depends(get_session)):
    return crud.get_habit_by_id(habit_id, db)

@router.get("/habits/by-name/{habit_name}", response_model=s.HabitSummary)
async def get_habit_by_name(habit_name: str, db: Session = Depends(get_session)):
    return crud.get_habit_by_name(habit_name, db)

@router.get("/habits/complete/{habit_id}", response_model=s.HabitWithCompletions)
def get_habit_completion_dates(habit_id: int, db: Session = Depends(get_session)):
    return crud.get_habit_completion_dates(habit_id, db)

@router.get("/habits/complete/today/{habit_id}", response_model=s.HabitCompletionStatus)
def get_habit_completion_status(habit_id: int, db: Session = Depends(get_session)):
    return crud.get_habit_today_completion_status(habit_id, db)

@router.get("/users/", response_model=List[s.UserSummary])
def get_users(db: Session = Depends(get_session)):
    return crud.get_users(db)

@router.get("/users/{user_id}", response_model=s.UserSummary)
def get_user_by_id(user_id: int, db: Session = Depends(get_session)):
    return crud.get_user_by_id(user_id, db)

@router.get("/users/by-username/{username}", response_model=s.UserSummary)
def get_user_by_username(username: str, db: Session = Depends(get_session)):
    return crud.get_user_by_username(username, db)

# ------------------------------ DELETE ROUTES ------------------------------

@router.delete("/habits/{habit_id}", response_model=bool)
def delete_habit(habit_id: int, db: Session = Depends(get_session)):
    return crud.delete_habit(habit_id, db)

@router.delete("/users/{user_id}", response_model=bool)
def delete_user(user_id: int, db: Session = Depends(get_session)):
    return crud.delete_user(user_id, db)