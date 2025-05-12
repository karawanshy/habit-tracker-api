from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.models import User
import os
from fastapi import Depends, HTTPException, status
from jose import JWTError
from app.database import get_db

# Secret key and algorithm for JWT encoding
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Password hashing context using bcrypt
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer to handle token retrieval from request headers
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/login")

# ---------------------------- Authentication Function ----------------------------

def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticate a user by checking their username and password.

    This function retrieves the user from the database and verifies the provided password.

    Parameters:
    - username (str): The username of the user attempting to authenticate.
    - password (str): The password provided by the user to authenticate.
    - db (Session): The database session to query the users table.

    Returns:
    - User | bool: Returns the User object if authentication is successful, or False if failed.
    """
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or not user.verify_password(password):  # Verify the password
        return False
    return user

# ---------------------------- JWT Token Generation ----------------------------

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    """
    Create an access token (JWT) for a user.

    The token includes the username and user ID as the subject and custom claims, respectively.
    The token expiration time is set according to `expires_delta`.

    Parameters:
    - username (str): The username to include in the token.
    - user_id (int): The user ID to include in the token.
    - expires_delta (timedelta): The time period after which the token will expire.

    Returns:
    - str: The encoded JWT token.
    """
    encode = {"sub": username, "id": user_id}
    expires = datetime.now() + expires_delta  # Calculate expiration time
    encode.update({"exp": expires})  # Add expiration claim
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------------------- Dependency to Retrieve Current User ----------------------------

def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    """
    Retrieve the current authenticated user based on the provided JWT token.

    This function decodes the JWT token, validates the claims, and retrieves the user from the database.

    Parameters:
    - token (str): The JWT token from the request header (received from the client).
    - db (Session): The database session to query the users table.

    Returns:
    - User: The authenticated user object.
    
    Raises:
    - HTTPException: Raises 401 if token is invalid or the user cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        
        # Check if the token contains necessary claims
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        # JWTError will be raised if token decoding fails
        raise credentials_exception

    # Retrieve the user from the database using the username and user ID from the token
    user = db.exec(select(User).where(User.username == username, User.id == user_id)).first()
    
    if user is None:
        # Raise an exception if the user does not exist in the database
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency to ensure the current user has admin privileges.

    parameters:
    - user (User): The current authenticated user object.

    returns:
    - User: The authenticated user object if they are an admin.

    raises:
    - HTTPException: Raises 403 if the user does not have admin privileges.
        
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Admin access required"
        )
    return current_user
