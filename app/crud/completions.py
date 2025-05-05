from sqlmodel import Session, select
import app.schemas as s
from app.models import HabitCompletion
from app.utils import get_habit_of_user, get_today


def mark_habit_completed_today(habit_id: int, user_id: int, db: Session) -> s.HabitCompletionStatus:
    """
    Mark the given habit as completed for today, if not already marked.

    Parameters:
        habit_id (int): ID of the habit.
        user_id (int): ID of the user.
        db (Session): Database session.

    Returns:
        HabitCompletionStatus: Schema containing the habit's id, name and today's completion status.
    """
    # Ensure the user owns the habit
    db_habit = get_habit_of_user(habit_id, user_id, db)

    # Check if habit was already completed today
    existing_completion = db.exec(
        select(HabitCompletion)
        .where((HabitCompletion.habit_id == habit_id) & (HabitCompletion.date == get_today()))
    ).first()

    # If not completed, mark it as completed
    if not existing_completion:
        existing_completion = HabitCompletion(habit_id=habit_id, date=get_today(), status=True)
        db.add(existing_completion)

    # Save changes and return status
    db.commit()
    db.refresh(existing_completion)

    return s.HabitCompletionStatus(
        id=habit_id,
        name=db_habit.name,
        completed_today=True
    )

def get_habit_today_completion_status(habit_id: int, user_id:int, db: Session) -> s.HabitCompletionStatus:
    """
    Retrieve whether the specified habit has been completed today.

    Parameters:
        habit_id (int): ID of the habit.
        user_id (int): ID of the user.
        db (Session): Database session.

    Returns:
        HabitCompletionStatus: Schema containing the habit's id, name and today's completion status.
    """
    db_habit = get_habit_of_user(habit_id, user_id, db)

    # Check for today's completion entry
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
    """
    Get all the dates when the specified habit was marked as completed.

    Parameters:
        habit_id (int): ID of the habit.
        user_id (int): ID of the user.
        db (Session): Database session.

    Returns:
        HabitWithCompletions: Schema containing the habit's id, name and a list of completion dates.
    """
    db_habit = get_habit_of_user(habit_id, user_id, db)

    # Retrieve all completion records for the habit
    completion_dates = db.exec(
        select(HabitCompletion).
        where(HabitCompletion.habit_id == habit_id)
    ).all()

    return s.HabitWithCompletions(
        id=db_habit.id,
        name=db_habit.name,
        completed_dates=[completion.date for completion in completion_dates]
    )
