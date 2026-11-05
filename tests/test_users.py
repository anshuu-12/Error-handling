import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import users

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    users.fake_users_db.clear()
    users.user_id_counter = 1

def test_create_user_success_and_default_status():
    response = client.post("/users/", json={
        "name": "Ansh Rohit",
        "email": "ansh@example.com",
        "phone": "9876543210",
        "age": 22
    })
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "active"

def test_missing_required_fields():
    response = client.post("/users/", json={
        "name": "Ansh Rohit",
        "phone": "9876543210"
    })
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    fields = [err["field"] for err in body["errors"]]
    assert "email" in fields
    assert "age" in fields

def test_wrong_data_types():
    response = client.post("/users/", json={
        "name": "Ansh Rohit",
        "email": "ansh@example.com",
        "phone": "9876543210",
        "age": "twenty-two"
    })
    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "age"

def test_out_of_range_values():
    response = client.post("/users/", json={
        "name": "A",
        "email": "ansh@example.com",
        "phone": "12345",
        "age": 15
    })
    assert response.status_code == 422
    fields = [err["field"] for err in response.json()["errors"]]
    assert "name" in fields
    assert "phone" in fields
    assert "age" in fields

def test_user_does_not_exist():
    response = client.get("/users/999")
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "error"
    assert body["message"] == "User with ID 999 not found"

def test_duplicate_email_bad_request():
    payload = {
        "name": "Ansh Rohit",
        "email": "ansh@example.com",
        "phone": "9876543210",
        "age": 22
    }
    client.post("/users/", json=payload)
    response = client.post("/users/", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["message"]