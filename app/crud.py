from sqlmodel import Session
from schemas import HabitCreate, HabitCompletionStatus, HabitWithCompletions, HabitUpdate
from models import Habit, HabitCompletion
from typing import List
from datetime import date

# Helper function to get a habit
def get_habit(habit_id: int, db: Session) -> Habit:
    db_habit = db.get(Habit, habit_id)
    if not db_habit:
        raise ValueError(f"Habit with id {habit_id} not found.")
    return db_habit


def create_habit(habit: HabitCreate, db: Session) -> Habit:
    db_habit = Habit(
        **habit.model_dump(), 
        start_date=date.today()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def update_habit(habit_id: int, habit: HabitUpdate, db: Session) -> Habit:
    db_habit = get_habit(habit_id, db)
    
    habit_data = habit.model_dump()
    for key, value in habit_data.items():
        if value is not None:
            setattr(db_habit, key, value)

    db.commit()
    db.refresh(db_habit)
    return db_habit

def mark_habit_completed_today(habit_id: int, status: bool, db: Session) -> HabitCompletionStatus:
    existing_completion = db.exec(
    HabitCompletion.select()
    .where((HabitCompletion.habit_id == habit_id) & (HabitCompletion.date == date.today()))
    ).first()

    if existing_completion:
        existing_completion.status = status
    else:
        existing_completion = HabitCompletion(habit_id=habit_id, date=date.today(), status=status)
        db.add(existing_completion)

    db.commit()
    db.refresh(existing_completion)

    db_habit = get_habit(habit_id, db)
    return HabitCompletionStatus(
        id=habit_id,
        name=db_habit.name,
        completed_today=status
    )


def delete_habit(habit_id: int, db: Session) -> bool:
    db_habit = get_habit(habit_id, db)
    db.delete(db_habit)
    db.commit()
    return True

def get_habits(db: Session, skip: int = 0, limit: int = 30) -> List[Habit]:
    return db.exec(
        Habit.select().
        offset(skip).
        limit(limit)
    ).all()

def get_habit_by_id(habit_id: int, db: Session) -> Habit:
    return get_habit(habit_id, db)

def get_habit_by_name(name: str, db: Session) -> Habit:
    return db.exec(
        Habit.select().
        where(Habit.name == name)
    ).first()

def get_habit_today_completion_status(habit_id: int, db: Session) -> HabitCompletionStatus:
    habit = get_habit(habit_id, db)
    
    completed = db.exec(HabitCompletion.select()
                               .where(
                                    (HabitCompletion.habit_id == habit_id) & 
                                    (HabitCompletion.date == date.today()))
        ).first()
    
    return HabitCompletionStatus(
        id=habit.id,
        name=habit.name,
        completed_today=completed.status if completed else False
    )

def get_habit_completion_dates(habit_id: int, db: Session) -> HabitWithCompletions:
    db_habit = get_habit(habit_id, db)
    
    completion_dates = db.exec(
        HabitCompletion.select().
        where(HabitCompletion.habit_id == habit_id)
    ).all()

    return HabitWithCompletions(
        id=db_habit.id,
        name=db_habit.name,
        completed_dates=[completion.date for completion in completion_dates]
    )