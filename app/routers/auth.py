from fastapi import APIRouter, Depends, HTTPException
from app.database import get_session
import app.schemas as s
from app.models import User
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth import authenticate_user, create_access_token, get_current_user

router = APIRouter()

@router.post("/login", response_model=s.UserLoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate user.")
    
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return s.UserLoginResponse(
        username=user.username,
        access_token=token,
        token_type="bearer"
    )

@router.get("/secure-data")
def secure_endpoint(current_user: User = Depends(get_current_user)):
    return {
        "msg": f"You're authenticated as {current_user.username}!"
    }