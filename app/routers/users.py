from fastapi import APIRouter, Depends
from app.database import get_session
import app.schemas as s
from app.models import User
import app.crud.users as crud
from typing import List
from sqlmodel import Session
from app.auth import get_current_user

router = APIRouter()

# ------------------------------ POST ROUTES ------------------------------
@router.post("/", response_model=s.UserSummary, status_code=201)
async def create_user(user: s.UserCreate, db: Session = Depends(get_session)):
    return crud.create_user(user, db)

# ------------------------------ PUT ROUTES ------------------------------
@router.put("/me", response_model=s.UserSummary)
async def update_user(user: s.UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return crud.update_user(user, current_user.id, db)

# ------------------------------ GET ROUTES ------------------------------
@router.get("/", response_model=List[s.UserSummary])
def get_users(db: Session = Depends(get_session)):
    return crud.get_users(db)

@router.get("/{user_id}", response_model=s.UserSummary)
def get_user_by_id(user_id: int, db: Session = Depends(get_session)):
    return crud.get_user_by_id(user_id, db)

@router.get("/by-username/{username}", response_model=s.UserSummary)
def get_user_by_username(username: str, db: Session = Depends(get_session)):
    return crud.get_user_by_username(username, db)

# ------------------------------ DELETE ROUTES ------------------------------
@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    crud.delete_user(user_id, current_user.id, db)
    return {"success": True}
