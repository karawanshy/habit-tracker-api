from tests.conftest_crud import db_user_factory
from uuid import uuid4
from app.crud import users as crud
from app.schemas import UserCreate, UserUpdate
from sqlmodel import Session
from pydantic import ValidationError
from fastapi import HTTPException
import pytest

def test_create_user(db_user_factory):
    user = db_user_factory()

    assert 'regular_user' in user.username
    assert user.email == "user@example.com"

def test_create_admin_user(db_user_factory):
    user = db_user_factory(is_admin=True)

    assert 'admin_user' in user.username
    assert user.email == "admin@example.com"

def test_create_user_with_invalid_email(db_user_factory, session: Session):
    with pytest.raises(ValidationError) as excinfo:
        user_data = UserCreate(
            username=f"regular_user_{uuid4()}",
            email="invalid_email",  # Invalid email
            password="password123",
            is_admin=False
        )
        crud.create_user(user_data, session)

    assert "value is not a valid email address" in str(excinfo.value)

def test_update_user(db_user_factory, session: Session):
    user = db_user_factory()

    updated_data = UserUpdate(
        username=f"updated_user_{uuid4()}"
    )

    user_summary = crud.update_user(updated_data, user.id, session)

    assert user_summary.id == user.id
    assert user_summary.username == updated_data.username
    assert user_summary.email == user.email

def test_update_user_with_invalid_email(db_user_factory, session: Session):
    user = db_user_factory()

    with pytest.raises(ValidationError) as excinfo:
        updated_data = UserCreate(
            email="invalid_email"  # Invalid email
        )
        crud.update_user(updated_data, user.id, session)

    assert "value is not a valid email address" in str(excinfo.value)

def test_update_user_with_id_not_found(db_user_factory, session: Session):
    updated_data = UserUpdate(
        username=f"updated_user_{uuid4()}"
    )

    with pytest.raises(HTTPException) as excinfo:
        crud.update_user(updated_data, 99999, session)  # Nonexistent ID

    assert excinfo.value.status_code == 404
    assert "not found" in str(excinfo.value)

def test_get_users(db_user_factory, session: Session):
    user = db_user_factory()

    users = crud.get_users(session)

    assert isinstance(users, list)
    assert len(users) > 0
    assert users[0].id == user.id
    assert users[0].username == user.username
    assert users[0].email == user.email

def test_get_user_by_id(db_user_factory, session: Session):
    user = db_user_factory()

    user_summary = crud.get_user_by_id(user.id, session)

    assert user_summary.id == user.id
    assert user_summary.username == user.username
    assert user_summary.email == user.email

def test_get_user_by_id_not_found(session: Session):
    with pytest.raises(HTTPException) as excinfo:
        crud.get_user_by_id(99999, session)  # Nonexistent ID

    assert excinfo.value.status_code == 404
    assert "not found" in str(excinfo.value)

def test_get_user_by_username(db_user_factory, session: Session):
    user = db_user_factory()

    user_summary = crud.get_user_by_username(user.username, session)

    assert user_summary.id == user.id
    assert user_summary.username == user.username
    assert user_summary.email == user.email

def test_get_user_by_username_not_found(session: Session):
    with pytest.raises(HTTPException) as excinfo:
        crud.get_user_by_username("nonexistent_user", session)  # Nonexistent username

    assert excinfo.value.status_code == 404
    assert "not found" in str(excinfo.value)

def test_delete_user(db_user_factory, session: Session):
    user = db_user_factory()

    response = crud.delete_user(user.id, session)

    assert response is True

    with pytest.raises(HTTPException) as excinfo:
        crud.get_user_by_id(user.id, session)  # Check if user is deleted

    assert excinfo.value.status_code == 404
    assert "not found" in str(excinfo.value)

def test_delete_user_not_found(session: Session):
    with pytest.raises(HTTPException) as excinfo:
        crud.delete_user(99999, session)  # Nonexistent ID

    assert excinfo.value.status_code == 404
    assert "not found" in str(excinfo.value)
