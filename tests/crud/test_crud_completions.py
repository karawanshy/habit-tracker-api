from tests.conftest_crud import db_habit_factory, db_user_factory
from app.crud import completions as crud
from sqlmodel import Session
from datetime import date
from fastapi import HTTPException
import pytest

def test_mark_habit_completed_today(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    completion_status = crud.mark_habit_completed_today(habit.id, user['id'], session)

    assert completion_status.id == habit.id
    assert completion_status.name == habit.name
    assert completion_status.completed_today is True

def test_mark_habit_completed_today_by_another_user(session: Session, db_habit_factory, db_user_factory):
    habit, user = db_habit_factory()

    # Create another user
    another_user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        # Attempt to mark the habit as completed by another user
        crud.mark_habit_completed_today(habit.id, another_user.id, session)
    
    assert excinfo.value.status_code == 404
    assert "not authorized" in excinfo.value.detail

def test_mark_habit_completed_today_not_found(session: Session, db_user_factory):
    user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        # Attempt to mark a non-existent habit as completed
        crud.mark_habit_completed_today(9999, user.id, session)
    
    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail

def test_mark_habit_completed_today_already_marked(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    # First mark the habit as completed
    crud.mark_habit_completed_today(habit.id, user['id'], session)

    # Try marking it again
    completion_status = crud.mark_habit_completed_today(habit.id, user['id'], session)

    assert completion_status.id == habit.id
    assert completion_status.name == habit.name
    assert completion_status.completed_today is True

def test_get_habit_today_completion_status(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    # First mark the habit as completed
    crud.mark_habit_completed_today(habit.id, user['id'], session)

    completion_status = crud.get_habit_today_completion_status(habit.id, user['id'], session)

    assert completion_status.id == habit.id
    assert completion_status.name == habit.name
    assert completion_status.completed_today in [True, False]

def test_get_habit_today_completion_status_by_another_user(session: Session, db_habit_factory, db_user_factory):
    habit, user = db_habit_factory()

    # Create another user
    another_user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        # Attempt to get completion status for a habit owned by another user
        crud.get_habit_today_completion_status(habit.id, another_user.id, session)
    
    assert excinfo.value.status_code == 404
    assert "not authorized" in excinfo.value.detail 

def test_get_habit_today_completion_status_not_found(session: Session, db_user_factory):
    user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        # Attempt to get completion status for a non-existent habit
        crud.get_habit_today_completion_status(9999, user.id, session)
    
    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail

def test_get_habit_completion_dates(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    # Mark the habit as completed
    crud.mark_habit_completed_today(habit.id, user['id'], session)

    response = crud.get_habit_completion_dates(habit.id, user['id'], session)

    assert isinstance(response.completed_dates, list)
    assert len(response.completed_dates) > 0
    assert response.completed_dates[0] == date.today()

def test_get_habit_with_no_completion_dates(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    response = crud.get_habit_completion_dates(habit.id, user['id'], session)

    assert isinstance(response.completed_dates, list)
    assert len(response.completed_dates) == 0

def test_get_habit_completion_dates_by_another_user(session: Session, db_habit_factory, db_user_factory):
    habit, user = db_habit_factory()

    # Create another user
    another_user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        # Attempt to get completion dates for a habit owned by another user
        crud.get_habit_completion_dates(habit.id, another_user.id, session)
    
    assert excinfo.value.status_code == 404
    assert "not authorized" in excinfo.value.detail
    
def test_get_habit_completion_dates_not_found(session: Session, db_user_factory):
    user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        # Attempt to get completion dates for a non-existent habit
        crud.get_habit_completion_dates(9999, user.id, session)
    
    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail
