from sqlmodel import Session
from schemas import HabitCreate, HabitCompletionStatus, HabitUpdate
from models import Habit, HabitCompletion
from typing import List
from datetime import date


def create_habit(db: Session, habit: HabitCreate) -> Habit:
    db_habit = Habit(
        **habit.model_dump(), 
        start_date=date.today()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def get_habits(db: Session, skip: int = 0, limit: int = 30) -> List[Habit]:
    return db.exec(
        Habit.select().
        offset(skip).
        limit(limit)
    ).all()

def get_habit_by_id(db: Session, habit_id: int) -> Habit:
    habit =  db.get(Habit, habit_id)
    return habit if habit else None

def get_habit_by_name(db: Session, name: str) -> Habit:
    habit = db.exec(
        Habit.select().
        where(Habit.name == name)
    ).first()
    return habit if habit else None

def get_habit_today_completion_status(db: Session, habit_id: int) -> bool:
    completion_Status = db.exec(HabitCompletion.select()
                               .where(
                                    (HabitCompletion.habit_id == habit_id) & 
                                    (HabitCompletion.date == date.today()))
        ).first()
    if completion_Status and completion_Status.date == date.today():
        return True
    return False

def get_habit_completion_dates(db: Session, habit_id: int) -> List[date]:
    completion_dates = db.exec(
        HabitCompletion.select().
        where(HabitCompletion.habit_id == habit_id)
    ).all()
    return [completion.date for completion in completion_dates]

def update_habit(db: Session, habit_id: int, habit: HabitUpdate) -> Habit:
    db_habit = db.get(Habit, habit_id)
    if not db_habit:
        return None
    habit_data = habit.model_dump()
    for key, value in habit_data.items():
        if value is not None:
            setattr(db_habit, key, value)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def update_habit_completion_status(db: Session, habit_id: int) -> HabitCompletionStatus:
    new_completion = HabitCompletion(habit_id=habit_id, date=date.today())
    db.add(new_completion)
    db.commit()
    db.refresh(new_completion)
    db_habit = db.get(Habit, habit_id)
    return HabitCompletionStatus(
        id=habit_id,
        name=db_habit.name,
        completed_today=True
    )


def delete_habit(db: Session, habit_id: int) -> bool:
    db_habit = db.get(Habit, habit_id)
    if not db_habit:
        return False
    db.delete(db_habit)
    db.commit()
    return True