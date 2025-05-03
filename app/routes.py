from fastapi import APIRouter, Depends
from app.database import get_session
from app.schemas import HabitCreate, HabitUpdate, HabitSummary, HabitWithCompletions, HabitCompletionStatus
import app.crud as crud
from typing import List
from sqlmodel import Session

router = APIRouter()

# ------------------------------ POST ROUTES ------------------------------

@router.post("/habits/", response_model=HabitSummary)
async def create_habit(habit: HabitCreate, db: Session = Depends(get_session)):
    return crud.create_habit(habit, db)

@router.post("/habits/{habit_id}", response_model=HabitSummary)
async def update_habit(habit_id: int, habit: HabitUpdate, db: Session = Depends(get_session)):
    return crud.update_habit(habit_id, habit, db)

@router.post("/habits/complete/today/{habit_id}", response_model=HabitCompletionStatus)
async def mark_habit_completed_today(habit_id: int, status: bool, db: Session = Depends(get_session)):
    return crud.mark_habit_completed_today(habit_id, status, db)

# ------------------------------ GET ROUTES ------------------------------

@router.get("/habits/", response_model=List[HabitSummary])
async def get_habits(db: Session = Depends(get_session)):
    return crud.get_habits(db)

@router.get("/habits/{habit_id}", response_model=HabitSummary)
async def get_habit_by_id(habit_id: int, db: Session = Depends(get_session)):
    return crud.get_habit_by_id(habit_id, db)

@router.get("/habits/by-name/{habit_name}", response_model=HabitSummary)
async def get_habit_by_name(habit_name: str, db: Session = Depends(get_session)):
    return crud.get_habit_by_name(habit_name, db)

@router.get("/habits/complete/{habit_id}", response_model=HabitWithCompletions)
def get_habit_completion_dates(habit_id: int, db: Session = Depends(get_session)):
    return crud.get_habit_completion_dates(habit_id, db)

@router.get("/habits/complete/today/{habit_id}", response_model=HabitCompletionStatus)
def get_habit_completion_status(habit_id: int, db: Session = Depends(get_session)):
    return crud.get_habit_today_completion_status(habit_id, db)

# ------------------------------ DELETE ROUTES ------------------------------

@router.delete("/habits/{habit_id}", response_model=bool)
def delete_habit(habit_id: int, db: Session = Depends(get_session)):
    return crud.delete_habit(habit_id, db)
