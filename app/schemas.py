from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, time
from models import HabitBase, HabitCompletionBase, Category, Frequency

# ------------------------------ SHARED FIELDS ------------------------------

class HabitAttributes(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = Field(default=Category.GENERAL)
    frequency: Optional[Frequency] = None
    reminder_time: Optional[time] = None

    @field_validator('category', mode='before')
    def validate_category(cls, value):
        if isinstance(value, str):
            value = value.strip().title()
        return Category(value)

    @field_validator('frequency', mode='before')
    def validate_frequency(cls, value):
        if isinstance(value, str):
            value = value.strip().title()
        return Frequency(value)
    
# ------------------------------ INPUT SCHEMAS ------------------------------

class HabitCreate(HabitAttributes):
    name: str
    frequency: Frequency

class HabitUpdate(HabitAttributes):
    pass

class HabitCompletionCreate(HabitCompletionBase):
    completed_today: bool = Field(default=False)

# ------------------------------ OUTPUT SCHEMAS ------------------------------  

class HabitInfoBase(BaseModel):
    id: int
    name: str

# Used to show a summary of a habit
class HabitSummary(HabitInfoBase):
    description: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    start_date: date
    reminder_time: Optional[time] = None
    completed_today: bool

# Used to show if a habit is completed today (by ID or name)
class HabitCompletionStatus(HabitInfoBase):
    completed_today: bool = Field(default=False)

# Used to show all completion dates for a specific habit
class HabitWithCompletions(HabitInfoBase):
    completed_dates: Optional[List[date]] = None