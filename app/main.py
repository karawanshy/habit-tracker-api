from fastapi import FastAPI, Depends
from app.database import init_db
from app.routers import users, habits, auth
from contextlib import asynccontextmanager
from app.auth import get_current_user
from app.models import User
from app.schemas import UserResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    init_db()
    print("Database initialized.")
    yield
    print("Shutting down Habit Tracker API.")

app = FastAPI(title="Habit Tracker API", lifespan=lifespan)

# Set custom OpenAPI with OAuth2 security
#app.openapi = lambda: custom_openapi(app)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(auth.router, tags=["Auth"])


@app.get("/", response_model=UserResponse)
async def root(current_user: User = Depends(get_current_user)):
    return current_user