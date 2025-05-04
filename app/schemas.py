from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, time
from app.models import HabitCompletionBase, Category, Frequency
from app.utils import normalize_category, normalize_frequency

# ------------------------------ SHARED DETAILES ------------------------------
    
class HabitDetails(BaseModel):
    description: Optional[str] = None
    category: Optional[Category] = None
    frequency: Optional[Frequency] = None
    reminder_time: Optional[time] = None

    @field_validator('category', mode='before')
    def validate_category(cls, value):
        return normalize_category(value)

    @field_validator('frequency', mode='before')
    def validate_frequency(cls, value):
        return normalize_frequency(value)
    
# ------------------------------ INPUT SCHEMAS ------------------------------

class HabitCreate(HabitDetails):
    name: str
    category: Optional[Category] = Field(default=Category.GENERAL)
    frequency: Frequency

class HabitUpdate(HabitDetails):
    name: Optional[str] = None

class HabitCompletionCreate(HabitCompletionBase):
    completed_today: bool = Field(default=False)

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

# ------------------------------ OUTPUT SCHEMAS ------------------------------  

class HabitBasicInfo(BaseModel):
    id: int
    name: str

# Used to show a summary of a habit
class HabitSummary(HabitBasicInfo, HabitDetails):
    start_date: date

    class Config:
        orm_mode = True

# Used to show if a habit is completed today (by ID or name)
class HabitCompletionStatus(HabitBasicInfo):
    completed_today: bool = Field(default=False)

# Used to show all completion dates for a specific habit
class HabitWithCompletions(HabitBasicInfo):
    completed_dates: Optional[List[date]] = None

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class UserSummary(UserResponse):
    email: str
    habits: List[HabitBasicInfo] = []

    class Config:
        orm_mode = True

class UserLoginResponse(BaseModel):
    username: str
    access_token: str
    token_type: str