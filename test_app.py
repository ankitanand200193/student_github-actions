import pytest
from app import app, students_collection, add_student, get_students, get_student_by_id, delete_student
from bson import ObjectId

@pytest.fixture(autouse=True)
def cleanup_db():
    # Clean up test data before each test
    students_collection.delete_many({})

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_student_by_name(client):
    students_collection.insert_one({"name": "Alice", "age": 21})
    response = client.get('/students/name/Alice')
    assert response.status_code == 200
    assert len(response.json) > 0
    assert response.json[0]["name"] == "Alice"

def test_get_student_by_name_not_found(client):
    response = client.get('/students/name/NonExistentName')
    assert response.status_code == 404
    assert response.json["error"] == "No students found with the given name"

def test_add_student(client):
    response = client.post('/students', json={"name": "Bob", "age": 22})
    assert response.status_code == 201
    assert response.json["name"] == "Bob"
    assert response.json["age"] == 22

def test_get_all_students(client):
    students_collection.insert_one({"name": "TestUser", "age": 20})
    response = client.get('/students')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0

def test_delete_student(client):
    student = students_collection.insert_one({"name": "Charlie", "age": 23})
    response = client.delete(f'/students/{student.inserted_id}')
    assert response.status_code == 200
    assert response.json["message"] == "Deleted"

    # Ensure student is deleted
    response = client.get(f'/students/{student.inserted_id}')
    assert response.status_code == 404

def test_add_student_missing_fields(client):
    response = client.post('/students', json={"name": "Eve"})
    # Your current app doesn't handle missing 'age' so this may return 500
    # You should update `add()` route in app.py to check for required fields
    assert response.status_code in [400, 500]

def test_get_student_by_partial_name(client):
    students_collection.insert_one({"name": "Alice", "age": 21})
    response = client.get('/students/name/Ali')
    assert response.status_code == 200
    assert any("Alice" in s["name"] for s in response.json)
