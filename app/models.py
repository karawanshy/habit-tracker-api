from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, ForeignKey
from datetime import datetime, date, time, timezone
from typing import Optional, List
from pydantic import EmailStr
import bcrypt
from passlib.hash import bcrypt

# -------------------------- Enum Classes --------------------------

class Category(str, Enum):
    """
    Enum representing different habit categories.
    Each habit can be classified under one of these categories.
    """
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
    """
    Enum representing the frequency of habit repetition.
    Habits can be set to repeat on a daily, weekly, monthly, or yearly basis.
    """
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

# -------------------------- Habit Completion Classes --------------------------

class HabitCompletionBase(SQLModel):
    """
    Base class for HabitCompletion, defining the common fields for habit completion records.
    Tracks the completion date and status of a habit.
    """
    date: date
    status: bool = Field(default=False)  # Indicates if the habit was completed
    habit_id: int = Field(sa_column=Column(Integer, ForeignKey("habit.id", ondelete="CASCADE"), nullable=False))

class HabitCompletion(HabitCompletionBase, table=True):
    """
    Represents a specific habit completion record in the database.
    Contains the completion status for a habit on a particular date.
    """
    id: int = Field(default=None, primary_key=True)
    habit: "Habit" = Relationship(back_populates="completed_dates")

# -------------------------- Habit Classes --------------------------

class HabitBase(SQLModel):
    """
    Base class for Habit, containing the core fields that define a habit.
    """
    name: str
    description: Optional[str] = None  # Optional description of the habit
    category: Optional[Category] = Field(default=Category.GENERAL)  # Default to 'General' if no category specified
    frequency: Frequency  # Frequency of the habit (Daily, Weekly, etc.)
    start_date: date  # The start date for the habit
    reminder_time: Optional[time] = None  # Optional reminder time for the habit
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False))

class Habit(HabitBase, table=True):
    """
    Represents a habit in the database. Extends HabitBase and includes relationships
    for habit completion records and the associated user.
    """
    id: int = Field(default=None, primary_key=True)
    completed_dates: List[HabitCompletion] = Relationship(back_populates="habit")
    user: "User" = Relationship(back_populates="habits")

    def __repr__(self):
        """
        Custom string representation of the Habit object.
        Includes whether the habit was completed today.
        """
        completed_today = any(completion.date == date.today() for completion in self.completed_dates or [])
        return (f"Habit(id={self.id}, name='{self.name}', category='{self.category}', "
                f"frequency='{self.frequency}', start_date={self.start_date}, "
                f"completed_today={completed_today})")

# -------------------------- User Classes --------------------------

class UserBase(SQLModel):
    """
    Base class for User, containing the core fields for user information.
    """
    username: str
    email: EmailStr  # Email should be validated as a proper email format

class User(UserBase, table=True):
    """
    Represents a user in the database. Extends UserBase and includes password management,
    relationship with habits, and utility methods for setting and verifying passwords.
    """
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    password: str  # The user's hashed password
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Timestamp of user creation
    habits: List[Habit] = Relationship(back_populates="user")

    def set_password(self, password: str):
        """
        Hashes and sets the user's password using passlib's bcrypt algorithm.

        Args:
        - password (str): The plain text password to be hashed.
        """
        self.password = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verifies a given password against the user's stored hashed password.

        Args:
        - password (str): The plain text password to verify.

        Returns:
        - bool: True if the password matches the stored hashed password, False otherwise.
        """
        return bcrypt.verify(password, self.password)

    def __repr__(self):
        """
        Custom string representation of the User object, excluding the password field for security.
        """
        return (f"User(id={self.id}, username='{self.username}', email='{self.email}')")
