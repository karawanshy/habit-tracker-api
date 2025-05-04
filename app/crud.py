from sqlmodel import Session, select
import app.schemas as s
from app.models import User, Habit, HabitCompletion, Category, Frequency
from app.utils import get_habit, normalize_name, normalize_username, get_user
from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status

# Create a HabitSummary schema from a Habit ORM model.
def create_habit_summary(habit: Habit) -> s.HabitSummary:
    return s.HabitSummary(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        category=habit.category,
        frequency=habit.frequency,
        reminder_time=habit.reminder_time,
        start_date=habit.start_date,
    )

# Create a UserSummary schema from a User ORM model.
def create_user_summary(user: User) -> s.UserSummary:
    return s.UserSummary(
        id=user.id,
        username=user.username,
        email=user.email,
        habits= [ s.HabitBasicInfo(id=habit.id, name=habit.name) for habit in user.habits ] if user.habits else []
    )

def create_habit(habit: s.HabitCreate, db: Session) -> s.HabitSummary:
    db_habit = Habit(
        **habit.model_dump(exclude={"name"}),
        name=normalize_name(habit.name),
        start_date=date.today()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)

    return create_habit_summary(db_habit)

def update_habit(habit_id: int, habit: s.HabitUpdate, db: Session) -> s.HabitSummary:
    db_habit = get_habit(habit_id, db)
    
    habit_data = habit.model_dump()
    for key, value in habit_data.items():
        if value is not None:
            setattr(db_habit, key, value)

    db.commit()
    db.refresh(db_habit)
    
    return create_habit_summary(db_habit)

def create_user(user: s.UserCreate, db: Session) -> s.UserSummary:
    db_user = User(
        username=normalize_username(user.username),
        email=user.email
    )
    db_user.set_password(user.hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return s.UserSummary(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
    )

def update_user(user_id: int, user: s.UserUpdate, db: Session) -> s.UserSummary:
    db_user = get_user(user_id, db)

    if user.username:
        db_user.username = user.username
    if user.hashed_password:
        db_user.set_password(user.hashed_password)
    if user.email:
        db_user.email = user.email

    db.commit()
    db.refresh(db_user)

    return create_user_summary(db_user)

def get_users(db: Session) -> List[s.UserSummary]:
    db_users = db.exec(
        select(User)
    ).all()

    return [ create_user_summary(user) for user in db_users ]

def get_user_by_id(user_id: int, db: Session) -> s.UserSummary:
    db_user = get_user(user_id, db)
    return create_user_summary(db_user)

def get_user_by_username(username: str, db: Session) -> s.UserSummary:
    username = normalize_username(username)
    db_user = db.exec(
        select(User).where(User.username == username)
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found."
        )

    return create_user_summary(db_user)

def delete_user(user_id: int, db: Session) -> bool:
    db_user = get_user(user_id, db)
    db.delete(db_user)
    db.commit()
    return True

def mark_habit_completed_today(habit_id: int, status: bool, db: Session) -> s.HabitCompletionStatus:
    if not isinstance(status, bool):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status value: {status}. It must be a boolean."
        )
    
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
    return s.HabitCompletionStatus(
        id=habit_id,
        name=db_habit.name,
        completed_today=status
    )


def delete_habit(habit_id: int, db: Session) -> bool:
    db_habit = get_habit(habit_id, db)
    db.delete(db_habit)
    db.commit()
    return True

def get_habit_today_completion_status(habit_id: int, db: Session) -> s.HabitCompletionStatus:
    db_habit = get_habit(habit_id, db)
    
    completed = db.exec(select(HabitCompletion)
                               .where(
                                    (HabitCompletion.habit_id == habit_id) & 
                                    (HabitCompletion.date == date.today()))
        ).first()
    
    return s.HabitCompletionStatus(
        id=db_habit.id,
        name=db_habit.name,
        completed_today=completed.status if completed else False
    )

def get_habits(db: Session, category: Optional[Category] = None, frequency: Optional[Frequency] = None) -> List[s.HabitSummary]:
    statement = select(Habit)

    if category:
        statement = statement.where(Habit.category == category)
    if frequency:
        statement = statement.where(Habit.frequency == frequency)

    habits = db.exec(statement).all()

    return [ create_habit_summary(habit) for habit in habits ]

def get_habit_by_id(habit_id: int, db: Session) -> s.HabitSummary:
    db_habit =  get_habit(habit_id, db)
    return create_habit_summary(db_habit)

def get_habit_by_name(name: str, db: Session) -> s.HabitSummary:
    name = normalize_name(name)
    db_habit = db.exec(
        select(Habit).
        where(Habit.name == name)
    ).first()

    if not db_habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with name {name} not found."
        )
    
    return create_habit_summary(db_habit)

def get_habits_by_category(category: Category, db: Session) -> List[s.HabitSummary]:
    db_habits = db.exec(
        select(Habit).
        where(Habit.category == category)
    ).all()

    return [ create_habit_summary(habit) for habit in db_habits ]

def get_habits_by_frequency(frequency: Frequency, db: Session) -> List[s.HabitSummary]:
    db_habits = db.exec(
        select(Habit).
        where(Habit.frequency == frequency)
    ).all()

    return [ create_habit_summary(habit) for habit in db_habits ]

def get_habit_completion_dates(habit_id: int, db: Session) -> s.HabitWithCompletions:
    db_habit = get_habit(habit_id, db)
    
    completion_dates = db.exec(
        select(HabitCompletion).
        where(HabitCompletion.habit_id == habit_id)
    ).all()

    return s.HabitWithCompletions(
        id=db_habit.id,
        name=db_habit.name,
        completed_dates=[completion.date for completion in completion_dates]
    )