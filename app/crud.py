from sqlmodel import Session, select
from app.schemas import HabitCreate, HabitCompletionStatus, HabitWithCompletions, HabitUpdate, HabitSummary
from app.models import Habit, HabitCompletion
from typing import List
from datetime import date

# Helper function to get a habit
def get_habit(habit_id: int, db: Session) -> Habit:
    db_habit = db.get(Habit, habit_id)
    if not db_habit:
        raise ValueError(f"Habit with id {habit_id} not found.")
    return db_habit

def create_habit_summary(habit: Habit) -> HabitSummary:
    return HabitSummary(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        category=habit.category,
        frequency=habit.frequency,
        reminder_time=habit.reminder_time,
        start_date=habit.start_date,
    )

def create_habit(habit: HabitCreate, db: Session) -> HabitSummary:
    db_habit = Habit(
        **habit.model_dump(), 
        start_date=date.today()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)

    return create_habit_summary(db_habit)

def update_habit(habit_id: int, habit: HabitUpdate, db: Session) -> HabitSummary:
    db_habit = get_habit(habit_id, db)
    
    habit_data = habit.model_dump()
    for key, value in habit_data.items():
        if value is not None:
            setattr(db_habit, key, value)

    db.commit()
    db.refresh(db_habit)
    
    return create_habit_summary(db_habit)

def mark_habit_completed_today(habit_id: int, status: bool, db: Session) -> HabitCompletionStatus:
    existing_completion = db.exec(
    select(HabitCompletion)
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

def get_habit_today_completion_status(habit_id: int, db: Session) -> HabitCompletionStatus:
    db_habit = get_habit(habit_id, db)
    
    completed = db.exec(select(HabitCompletion)
                               .where(
                                    (HabitCompletion.habit_id == habit_id) & 
                                    (HabitCompletion.date == date.today()))
        ).first()
    
    return HabitCompletionStatus(
        id=db_habit.id,
        name=db_habit.name,
        completed_today=completed.status if completed else False
    )

def get_habits(db: Session, skip: int = 0, limit: int = 30) -> List[HabitSummary]:
    habits = db.exec(
        select(Habit).
        offset(skip).
        limit(limit)
    ).all()

    return [ create_habit_summary(habit) for habit in habits ]

def get_habit_by_id(habit_id: int, db: Session) -> HabitSummary:
    db_habit =  get_habit(habit_id, db)
    return create_habit_summary(db_habit)

def get_habit_by_name(name: str, db: Session) -> HabitSummary:
    db_habit = db.exec(
        select(Habit).
        where(Habit.name == name)
    ).first()

    if db_habit is None:
        raise ValueError(f"Habit with name '{name}' not found.")
    
    return create_habit_summary(db_habit)


def get_habit_completion_dates(habit_id: int, db: Session) -> HabitWithCompletions:
    db_habit = get_habit(habit_id, db)
    
    completion_dates = db.exec(
        select(HabitCompletion).
        where(HabitCompletion.habit_id == habit_id)
    ).all()

    return HabitWithCompletions(
        id=db_habit.id,
        name=db_habit.name,
        completed_dates=[completion.date for completion in completion_dates]
    )