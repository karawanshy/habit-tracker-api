from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import users, habits, auth
from contextlib import asynccontextmanager
from app.openapi_config import custom_openapi

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    init_db()
    print("Database initialized.")
    yield
    print("Shutting down Habit Tracker API.")

app = FastAPI(title="Habit Tracker API", lifespan=lifespan)

# Set custom OpenAPI with OAuth2 security
app.openapi = lambda: custom_openapi(app)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(auth.router, tags=["Auth"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Habit Tracker API!"}