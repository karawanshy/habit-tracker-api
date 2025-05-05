from sqlmodel import Session, select
import app.schemas as s
from app.models import Habit, Category, Frequency
from app.utils import get_habit_of_user, normalize_name
from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status
from app.crud.serializers import create_habit_summary

def create_habit(habit: s.HabitCreate, user_id: int, db: Session) -> s.HabitSummary:
    db_habit = Habit(
        **habit.model_dump(exclude={"name"}),
        name=normalize_name(habit.name),
        user_id=user_id,
        start_date=date.today()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)

    return create_habit_summary(db_habit)

def update_habit(habit_id: int, habit: s.HabitUpdate, user_id: int, db: Session) -> s.HabitSummary:
    db_habit = get_habit_of_user(habit_id, user_id, db)
    
    habit_data = habit.model_dump()
    for key, value in habit_data.items():
        if value is not None:
            setattr(db_habit, key, value)

    db.commit()
    db.refresh(db_habit)
    
    return create_habit_summary(db_habit)

def get_habits(db: Session, user_id: int, category: Optional[Category] = None, frequency: Optional[Frequency] = None) -> List[s.HabitSummary]:
    query = select(Habit).where(Habit.user_id == user_id)

    if category:
        query = query.where(Habit.category == category)
    if frequency:
        query = query.where(Habit.frequency == frequency)

    habits = db.exec(query).all()

    return [ create_habit_summary(habit) for habit in habits ]

def get_habit_by_id(habit_id: int, user_id: int, db: Session) -> s.HabitSummary:
    db_habit =  get_habit_of_user(habit_id, user_id, db)
    return create_habit_summary(db_habit)

def get_habit_by_name(name: str, user_id: int, db: Session) -> s.HabitSummary:
    name = normalize_name(name)
    db_habit = db.exec(
        select(Habit).
        where(Habit.user_id == user_id, Habit.name == name)
    ).first()

    if not db_habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with name {name} not found or not authorized."
        )
    
    return create_habit_summary(db_habit)


def delete_habit(habit_id: int, user_id: int, db: Session) -> bool:
    db_habit = get_habit_of_user(habit_id, user_id, db)
    db.delete(db_habit)
    db.commit()
    return True
