from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, ForeignKey
from datetime import datetime, date, time, timezone
from typing import Optional, List
from pydantic import EmailStr
import bcrypt
from passlib.hash import bcrypt

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
    status: bool = Field(default=False)
    habit_id: int = Field(sa_column=Column(Integer, ForeignKey("habit.id", ondelete="CASCADE"), nullable=False))

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
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False))
    
class Habit(HabitBase, table=True):
    id: int = Field(default=None, primary_key=True)
    completed_dates: List[HabitCompletion] = Relationship(back_populates="habit")
    user: "User" = Relationship(back_populates="habits")

    def __repr__(self):
        completed_today = any(completion.date == date.today() for completion in self.completed_dates or [])
        return (f"Habit(id={self.id}, name='{self.name}', category='{self.category}', "
                f"frequency='{self.frequency}', start_date={self.start_date}, "
                f"completed_today={completed_today})")

    
class UserBase(SQLModel):
    username: str
    email: EmailStr

class User(UserBase, table=True):
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    habits: List[Habit] = Relationship(back_populates="user")
    
    def set_password(self, password: str):
        """Hashes and sets the user's password using passlib."""
        self.password = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verifies the password using passlib."""
        return bcrypt.verify(password, self.password)
        
    def __repr__(self):
        return (f"User(id={self.id}, username='{self.username}', email='{self.email}')")