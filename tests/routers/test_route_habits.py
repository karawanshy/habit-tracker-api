from fastapi.testclient import TestClient
from app.main import app
from datetime import date

def test_create_habit(habit_factory):
    habit = habit_factory()
    assert habit["name"].startswith("Read Books")
    assert habit["category"] == "Personal Development"
    assert habit["frequency"] == "Daily"
    assert "id" in habit

def test_create_habit_invalid_category(client: TestClient, regular_user_token):
    invalid_habit_data = {
        "name": "read books",
        "description": "Read 30 minutes daily",
        "category": "education",  # Invalid category
        "frequency": "daily"
    }

    response = client.post(
        "/habits/",
        json=invalid_habit_data,
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    # Assert that the status code is 400, indicating a bad request
    assert response.status_code == 400
   
    data = response.json()
    assert "detail" in data
    assert "category" in data["detail"]  # Check if 'category' is mentioned in the error message

def test_create_habit_invalid_frequency(client: TestClient, regular_user_token):
    invalid_habit_data = {
        "name": "read books",
        "description": "Read 30 minutes daily",
        "category": "personal development",
        "frequency": "hourly"  # Invalid frequency
    }

    response = client.post(
        "/habits/",
        json=invalid_habit_data,
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    # Assert that the status code is 400, indicating a bad request
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "frequency" in data["detail"]  # Check if 'category' is mentioned in the error message

def test_mark_habit_completed_today(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    # mark the habit as completed today
    response = client.post(
        f"/habits/complete/today/{habit_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["completed_today"] is True

def test_update_habit(client: TestClient, habit_factory, regular_user_token):
    habit = habit_factory()

    updated_habit_data = {
        "description": "Read 1 hour daily",
    }

    response = client.put(
        f"/habits/{habit['id']}",
        json=updated_habit_data,
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == habit["name"]
    assert data["description"] == "Read 1 hour daily"
    assert data["category"] == "Personal Development"
    assert data["frequency"] == "Daily"

def test_get_habits(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    response = client.get(
        "/habits/",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == habit_id

def test_get_habits_by_category(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    response = client.get(
        "/habits/?category=personal%20development",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == habit_id

def test_get_habits_by_frequency(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    response = client.get(
        "/habits/?frequency=daily",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == habit_id

def test_get_habits_by_category_and_frequency(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    response = client.get(
        "/habits/?category=personal%20development&frequency=daily",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == habit_id

def test_get_habit_by_id(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    response = client.get(
        f"/habits/{habit_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == habit_id
    assert data["name"].startswith("Read Books")
    assert data["description"] == "Read 30 minutes daily"
    assert data["category"] == "Personal Development"
    assert data["frequency"] == "Daily"

def test_get_habit_by_name(client: TestClient, habit_factory, regular_user_token):
    habit = habit_factory()

    response = client.get(
        f"/habits/by-name/{habit['name']}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == habit["id"]
    assert data["name"].startswith("Read Books")
    assert data["description"] == "Read 30 minutes daily"
    assert data["category"] == "Personal Development"
    assert data["frequency"] == "Daily"

def test_get_habit_completion_status(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    response = client.get(
        f"/habits/complete/today/{habit_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == habit_id
    assert "completed_today" in data

def test_get_habit_completion_dates(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]
    
    # Mark the habit as completed today
    response = client.post(
        f"/habits/complete/today/{habit_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    response = client.get(
        f"/habits/complete/{habit_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == habit_id
    assert "completed_dates" in data
    assert isinstance(data["completed_dates"], list)
    assert len(data["completed_dates"]) > 0

    today_str = date.today().isoformat()
    assert today_str in data["completed_dates"]

def test_delete_habit(client: TestClient, habit_factory, regular_user_token):
    habit_id = habit_factory()["id"]

    response = client.delete(
        f"/habits/{habit_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Habit deleted successfully."}

    # Verify the habit is deleted
    response = client.get(
        f"/habits/{habit_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )

    assert response.status_code == 404