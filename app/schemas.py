from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List
from datetime import date, time
from app.models import HabitCompletionBase, Category, Frequency
from app.utils import normalize_category, normalize_frequency
from pydantic import ConfigDict

# ------------------------------ SHARED DETAILS ------------------------------

class HabitDetails(BaseModel):
    """
    Base class for shared habit details like description, category, frequency, and reminder time.
    Used as a parent class for creating and updating habits.
    """
    description: Optional[str] = None 
    category: Optional[Category] = None
    frequency: Optional[Frequency] = None
    reminder_time: Optional[time] = None

    # Validator to normalize the category input before it's set
    @field_validator('category', mode='before')
    def validate_category(cls, value):
        return normalize_category(value)

    # Validator to normalize the frequency input before it's set
    @field_validator('frequency', mode='before')
    def validate_frequency(cls, value):
        return normalize_frequency(value)
    
# ------------------------------ INPUT SCHEMAS ------------------------------

class HabitCreate(HabitDetails):
    """
    Schema for creating a new habit. Inherits from HabitDetails and adds the required 'name' field.
    """
    name: str
    category: Optional[Category] = Field(default=Category.GENERAL)  # Default category if none is provided
    frequency: Frequency

class HabitUpdate(HabitDetails):
    """
    Schema for updating an existing habit. Only the name and optional details can be updated.
    """
    name: Optional[str] = None

class HabitCompletionCreate(HabitCompletionBase):
    """
    Schema for creating a habit completion record, indicating if the habit was completed today.
    """
    completed_today: bool = Field(default=False)

class UserCreate(BaseModel):
    """
    Schema for creating a new user, requiring a username, password, and email.
    """
    username: str  
    password: str  
    email: EmailStr
    is_admin: Optional[bool] = False  # Only for testing purposes; should not be set in production.

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user's information. Fields are optional for updating.
    """
    username: Optional[str] = None  
    password: Optional[str] = None
    email: Optional[str] = None

class UserLogin(BaseModel):
    """
    Schema for user login, requiring a username and password for authentication.
    """
    username: str 
    password: str 

# ------------------------------ OUTPUT SCHEMAS ------------------------------

class HabitBasicInfo(BaseModel):
    """
    Basic information about a habit, including its ID and name.
    Used for habit summaries or basic responses.
    """
    id: int  
    name: str 

# Used to show a summary of a habit, including start date and additional habit details
class HabitSummary(HabitBasicInfo, HabitDetails):
    """
    Extended habit information for displaying a summary of the habit,
    including the start date and details like description, category, and frequency.
    """
    start_date: date 

    model_config = ConfigDict(from_attributes=True)

# Used to show if a habit is completed today (by ID or name)
class HabitCompletionStatus(HabitBasicInfo):
    """
    Displays whether the habit was completed today.
    """
    completed_today: bool = Field(default=False) 
    
# Used to show all completion dates for a specific habit
class HabitWithCompletions(HabitBasicInfo):
    """
    Displays a list of all completion dates for a given habit.
    """
    completed_dates: Optional[List[date]] = None

class UserResponse(BaseModel):
    """
    Basic response for a user, including the user ID and username.
    """
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class UserSummary(UserResponse):
    """
    Extended user information for displaying user details along with their habits.
    """
    email: str
    habits: List[HabitBasicInfo] = []

    model_config = ConfigDict(from_attributes=True)

class UserLoginResponse(BaseModel):
    """
    Response schema for user login, including the username and access token.
    """
    username: str 
    access_token: str 
    token_type: str
