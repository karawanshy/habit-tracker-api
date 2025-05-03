from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, time
from app.models import HabitCompletionBase, Category, Frequency
from app.utils import normalize_category, normalize_frequency

# ------------------------------ SHARED DETAILES ------------------------------

class HabitDetails(BaseModel):
    description: Optional[str] = None
    category: Optional[Category] = Field(default=Category.GENERAL)
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
    frequency: Frequency

class HabitUpdate(HabitDetails):
    name: Optional[str] = None

class HabitCompletionCreate(HabitCompletionBase):
    completed_today: bool = Field(default=False)

# ------------------------------ OUTPUT SCHEMAS ------------------------------  

class HabitInfoBase(BaseModel):
    id: int
    name: str

# Used to show a summary of a habit
class HabitSummary(HabitInfoBase, HabitDetails):
    start_date: date

# Used to show if a habit is completed today (by ID or name)
class HabitCompletionStatus(HabitInfoBase):
    completed_today: bool = Field(default=False)

# Used to show all completion dates for a specific habit
class HabitWithCompletions(HabitInfoBase):
    completed_dates: Optional[List[date]] = None