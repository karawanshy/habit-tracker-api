from sqlmodel import Session, select
import app.schemas as s
from app.models import HabitCompletion
from app.utils import get_habit_of_user, get_today


def mark_habit_completed_today(habit_id: int, user_id: int, db: Session) -> s.HabitCompletionStatus:
    # Verify habit ownership
    db_habit = get_habit_of_user(habit_id, user_id, db)

    # Check for existing completion today
    existing_completion = db.exec(
    select(HabitCompletion)
    .where((HabitCompletion.habit_id == habit_id) & (HabitCompletion.date == get_today()))
    ).first()

    if not existing_completion:
        existing_completion = HabitCompletion(habit_id=habit_id, date=get_today(), status=True)
        db.add(existing_completion)

    db.commit()
    db.refresh(existing_completion)

    return s.HabitCompletionStatus(
        id=habit_id,
        name=db_habit.name,
        completed_today=True
    )

def get_habit_today_completion_status(habit_id: int, user_id:int, db: Session) -> s.HabitCompletionStatus:
    db_habit = get_habit_of_user(habit_id, user_id, db)
    
    completed = db.exec(select(HabitCompletion)
                               .where(
                                    (HabitCompletion.habit_id == habit_id) & 
                                    (HabitCompletion.date == get_today())
                        )).first()
    
    return s.HabitCompletionStatus(
        id=db_habit.id,
        name=db_habit.name,
        completed_today=completed.status if completed else False
    )

def get_habit_completion_dates(habit_id: int, user_id:int, db: Session) -> s.HabitWithCompletions:
    db_habit = get_habit_of_user(habit_id, user_id, db)
    
    completion_dates = db.exec(
        select(HabitCompletion).
        where(HabitCompletion.habit_id == habit_id)
    ).all()

    return s.HabitWithCompletions(
        id=db_habit.id,
        name=db_habit.name,
        completed_dates=[completion.date for completion in completion_dates]
    )
