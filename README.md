# 🧠 Habit Tracker API

A fully tested FastAPI-based backend service that allows users to track their habits, completion status, and progress — with full CRUD functionality, user authentication, and admin capabilities.

Built in **6 days** using modern Python tools and best practices. Fast, clean, and powerful.

---

## 🚀 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) – for blazing-fast API development  
- [Uvicorn](https://www.uvicorn.org/) – lightning-fast ASGI server  
- [SQLModel](https://sqlmodel.tiangolo.com/) – SQLAlchemy + Pydantic  
- [Alembic](https://alembic.sqlalchemy.org/) – schema migrations  
- [PostgreSQL](https://www.postgresql.org/) – rock-solid relational DB  
- [Pydantic](https://docs.pydantic.dev/) – data validation and serialization  
- [python-dotenv](https://pypi.org/project/python-dotenv/) – environment management  
- [JWT (python-jose)](https://github.com/mpdavis/python-jose) – secure token-based authentication  
- [Git](https://git-scm.com/) – version control  
- [Pytest](https://docs.pytest.org/) – testing framework

---

## ✨ Features

### 👥 User Management
- Create a user
- Update user info
- Delete own account
- **Admin-only**:
  - View all users
  - Get user by ID
  - Get user by username

### 🔐 Authentication
- JWT-based login via `/login`
- Secure endpoints require token in `Authorization: Bearer <token>`

### 📋 Habit Management (Authenticated Users Only)
- Create a habit
- Get all habits
  - Optional filtering by `category` and/or `frequency` (enums)
- Get habit by ID
- Get habit by name
- Update a habit
- Delete a habit

### ✅ Completion Tracking
- Mark a habit as completed **today**
- Get today's completion status
- Get all past completion dates

---

## 🧪 Tests

Structured and comprehensive test coverage for routers and CRUD logic.

### 📁 tests/routers
- `test_route_users.py`
- `test_route_habits.py`
- `test_route_auth.py`

### 📁 tests/crud
- `test_crud_users.py`
- `test_crud_habits.py`
- `test_crud_completions.py`

### 🧰 Fixtures & Helpers
- `conftest.py` – global test fixtures
- `conftest_crud.py` – CRUD-specific fixtures
- `test_helpers.py` – shared helper functions (e.g. token generation)

To run all tests:
```bash
pytest
```

## ⚙️ Setup Instructions
1. clone the repo
2. Create a PostgreSQL database
3. Create a `.env` file in the root with:
```python
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:<port>/<db>
SECRET_KEY=your-secret-key
```
4. Install dependencies
```bash
pip install -r requirements.txt
```
5. Run migrations
```bash
alembic upgrade head
```
6. Run the server
```bash
uvicorn app.main:app --reload
```
7. Open your browser at:
```bash
http://localhost:8000/docs
```
→ Interactive Swagger UI to test all endpoints 

## 🔐 Authentication
- POST to /login with valid user credentials
- You'll receive a JWT token
- Use this token for all authenticated endpoints:
```makefile
Authorization: Bearer <your_token_here>
```

## 🧠 Final Notes
- All habit endpoints require authentication.
- Admin routes are protected and require a user with is_admin=True.
- Thoroughly tested for edge cases, invalid inputs, and permission errors.

## 🚀 Future Plans

- Add user registration confirmation via email  
- Implement email reminders based on `reminder_time` and `frequency`  
- Provide user analytics and statistics for admins  
- Dockerize the application for easier deployment  

## 🧑‍💻 Author
##### Karawan Sh. Y.  
💻 Passionate backend developer

## 📜 License
MIT License. Use it, fork it, break it, improve it.