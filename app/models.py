from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, time
from typing import Optional, List

class Category(str, Enum):
    PERSONAL_DEVELOPMENT = "Personal Development"
    FITNESS = "Fitness"
    FINANCE = "Finance"
    NUTRITION = "Nutrition"
    SOCIAL = "Social"
    HOME_AND_ORGANIZATION = "Home and Organization"
    SELF_CARE = "Self Care"
    MENTAL_WELLNESS = "Mental Wellness"
    GENERAL = "General"

class Frequency(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class HabitCompletionBase(SQLModel):
    date: date
    habit_id: int = Field(foreign_key="habit.id")
    status: bool = Field(default=False)

class HabitCompletion(HabitCompletionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    habit: "Habit" = Relationship(back_populates="completed_dates")

class HabitBase(SQLModel):
    name: str
    description: Optional[str] = None
    category: Optional[Category] = Field(default=Category.GENERAL)
    frequency: Frequency
    start_date: date
    reminder_time: Optional[time] = None
    
class Habit(HabitBase, table=True):
    id: int = Field(default=None, primary_key=True)
    completed_dates: List[HabitCompletion] = Relationship(back_populates="habit")

    def __repr__(self):
        return (f"Habit(id={self.id}, name='{self.name}', category='{self.category}', "
                f"frequency='{self.frequency}', start_date={self.start_date}, "
                f"completed_today={any(self.completed_dates)})")