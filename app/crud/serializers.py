import app.schemas as s
from app.models import User, Habit

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