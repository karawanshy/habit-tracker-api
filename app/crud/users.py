from sqlmodel import Session, select
import app.schemas as s
from app.models import User
from app.utils import normalize_username, get_user
from typing import List
from fastapi import HTTPException, status
from app.crud.serializers import create_user_summary

def create_user(user: s.UserCreate, db: Session) -> s.UserSummary:
    db_user = User(
        username=normalize_username(user.username),
        email=user.email
    )
    db_user.set_password(user.password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return s.UserSummary(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
    )

def update_user(user: s.UserUpdate, user_id: int, db: Session) -> s.UserSummary:
    db_user = get_user(user_id, db)

    if user.username:
        db_user.username = user.username
    if user.password:
        db_user.set_password(user.password)
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
