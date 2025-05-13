from tests.conftest_crud import db_habit_factory, db_user_factory
from app.crud import habits as crud
from sqlmodel import Session
from app.schemas import HabitUpdate
import pytest
from fastapi import HTTPException

def test_create_habit(db_habit_factory):
    habit, user = db_habit_factory()

    assert habit.id is not None
    assert habit.frequency == "Daily"
    assert habit.category == "Personal Development"

def test_update_habit(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    updated_habit_data = HabitUpdate(
        description= "Read 1 hour daily",
    )

    habit_summary = crud.update_habit(habit.id, updated_habit_data, user['id'], session)

    assert habit_summary.id == habit.id
    assert habit_summary.description == "Read 1 hour daily"


def test_update_habit_for_other_user(session: Session, db_habit_factory, db_user_factory):
    habit, user = db_habit_factory()
    other_user = db_user_factory()

    updated_habit_data = HabitUpdate(
        description= "Read 1 hour daily",
    )

    with pytest.raises(HTTPException) as excinfo:
        crud.update_habit(habit.id, updated_habit_data, other_user.id, session)

    assert excinfo.value.status_code == 404
    assert "not authorized" in excinfo.value.detail


def test_get_habits(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    habits = crud.get_habits(session, user['id'])

    assert isinstance(habits, list)
    assert len(habits) > 0
    assert habits[0].id == habit.id
    assert habits[0].description == habit.description
    assert habits[0].frequency == habit.frequency
    assert habits[0].category == habit.category

def test_get_habits_by_category(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    habits = crud.get_habits(session, user['id'], habit.category)

    assert isinstance(habits, list)
    assert len(habits) > 0
    assert habits[0].id == habit.id
    assert habits[0].description == habit.description
    assert habits[0].frequency == habit.frequency
    assert habits[0].category == habit.category

def test_get_habits_by_frequency(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    habits = crud.get_habits(session, user['id'], frequency=habit.frequency)

    assert isinstance(habits, list)
    assert len(habits) > 0
    assert habits[0].id == habit.id
    assert habits[0].description == habit.description
    assert habits[0].frequency == habit.frequency
    assert habits[0].category == habit.category

def test_get_habits_by_category_and_frequency(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    habits = crud.get_habits(session, user['id'], habit.category, habit.frequency)

    assert isinstance(habits, list)
    assert len(habits) > 0
    assert habits[0].id == habit.id
    assert habits[0].description == habit.description
    assert habits[0].frequency == habit.frequency
    assert habits[0].category == habit.category 

def test_get_habit_by_id(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    habit_summary = crud.get_habit_by_id(habit.id, user['id'], session)

    assert habit_summary.id == habit.id
    assert habit_summary.description == habit.description
    assert habit_summary.frequency == habit.frequency
    assert habit_summary.category == habit.category 

def test_get_habit_by_id_for_other_user(session: Session, db_habit_factory, db_user_factory):
    habit, user = db_habit_factory()
    other_user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        crud.get_habit_by_id(habit.id, other_user.id, session)

    assert excinfo.value.status_code == 404
    assert "not authorized" in excinfo.value.detail

def test_get_habit_by_id_not_found(session: Session, db_user_factory):
    user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        crud.get_habit_by_id(99999, user.id, session)

    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail

def test_get_habit_by_name(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    habit_summary = crud.get_habit_by_name(habit.name, user['id'], session)

    assert habit_summary.id == habit.id
    assert habit_summary.description == habit.description
    assert habit_summary.frequency == habit.frequency
    assert habit_summary.category == habit.category

def test_get_habit_by_name_for_other_user(session: Session, db_habit_factory, db_user_factory):
    habit, user = db_habit_factory()
    other_user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        crud.get_habit_by_name(habit.name, other_user.id, session)

    assert excinfo.value.status_code == 404
    assert "not authorized" in excinfo.value.detail

def test_get_habit_by_name_not_found(session: Session, db_user_factory):
    user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        crud.get_habit_by_name("non_existent_habit", user.id, session)

    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail

def test_delete_habit(session: Session, db_habit_factory):
    habit, user = db_habit_factory()

    response = crud.delete_habit(habit.id, user['id'], session)

    assert response is True

    with pytest.raises(HTTPException) as excinfo:
        crud.get_habit_by_id(habit.id, user['id'], session)

    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail

def test_delete_habit_not_found(session: Session, db_user_factory):
    user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        crud.delete_habit(99999, user.id, session)

    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail

def test_delete_habit_for_other_user(session: Session, db_habit_factory, db_user_factory):
    habit, user = db_habit_factory()
    other_user = db_user_factory()

    with pytest.raises(HTTPException) as excinfo:
        crud.delete_habit(habit.id, other_user.id, session)

    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail
