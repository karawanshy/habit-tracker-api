import pytest
from app.models import User, Habit, Category, Frequency
from uuid import uuid4
from sqlmodel import Session
from app.crud import habits as crud_habits
from app.crud import users as crud_users

from app import crud, schemas as s  # Adjust based on your structure

@pytest.fixture
def db_user_factory(session: Session):
    def _create_user(is_admin=False):
        user_data = User(
            username=f"admin_user_{uuid4()}" if is_admin else f"regular_user_{uuid4()}",
            email="admin@example.com" if is_admin else "user@example.com",
            is_admin=is_admin,
        )
        user_data.set_password("password123")

        user_summary = crud_users.create_user(
            user=user_data,
            db=session
        )
        return user_summary
    return _create_user


@pytest.fixture
def db_habit_factory(session: Session, user_factory: callable):
    def _create_habit(is_admin=False):
        user = user_factory(is_admin=is_admin)

        habit_data = Habit(
            name=f"Read Books {uuid4()}",
            description="Read 30 minutes daily",
            category=Category.PERSONAL_DEVELOPMENT,
            frequency=Frequency.DAILY,
        )

        habit_summary = crud_habits.create_habit(
            habit=habit_data,
            user_id=user['id'],
            db=session
        )

        return habit_summary, user
    return _create_habit

