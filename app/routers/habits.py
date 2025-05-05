from fastapi import APIRouter, Depends, Query
from app.database import get_session
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
async def create_habit(habit: s.HabitCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return habits.create_habit(habit, current_user.id, db)

@router.post("/complete/today/{habit_id}", response_model=s.HabitCompletionStatus)
async def mark_habit_completed_today(habit_id: int, status: bool, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return completions.mark_habit_completed_today(habit_id, status, current_user.id, db)

# ------------------------------ PUT ROUTES ------------------------------
@router.put("/{habit_id}", response_model=s.HabitSummary)
async def update_habit(habit_id: int, habit: s.HabitUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return habits.update_habit(habit_id, habit, current_user.id, db)

# ------------------------------ GET ROUTES ------------------------------
@router.get("/", response_model=List[s.HabitSummary])
def get_habits(
    category: Optional[str] = Query(default=None, description=f"One of: {', '.join(c.value for c in Category)}"),
    frequency: Optional[str] = Query(default=None, description=f"One of: {', '.join(f.value for f in Frequency)}"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    return habits.get_habits(db,
                           user_id=current_user.id,
                           category=normalize_category(category),
                           frequency=normalize_frequency(frequency))

@router.get("/{habit_id}", response_model=s.HabitSummary)
async def get_habit_by_id(habit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return habits.get_habit_by_id(habit_id, current_user.id, db)

@router.get("/by-name/{habit_name}", response_model=s.HabitSummary)
async def get_habit_by_name(habit_name: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return habits.get_habit_by_name(habit_name, current_user.id, db)

@router.get("/complete/{habit_id}", response_model=s.HabitWithCompletions)
def get_habit_completion_dates(habit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return completions.get_habit_completion_dates(habit_id, current_user.id, db)

@router.get("/complete/today/{habit_id}", response_model=s.HabitCompletionStatus)
def get_habit_completion_status(habit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return completions.get_habit_today_completion_status(habit_id, current_user.id, db)

# ------------------------------ DELETE ROUTES ------------------------------
@router.delete("/{habit_id}")
def delete_habit(habit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    habits.delete_habit(habit_id, current_user.id, db)
    return {"success": True}