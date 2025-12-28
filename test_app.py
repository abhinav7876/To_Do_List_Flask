from app import app
import pytest
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200

def test_create_task_json(client):
    task = {
        "ID": 101,
        "title": "Test Task",
        "description": "Pytest task",
        "due_date": "2099-12-31",
        "status": "Pending"
    }
    response = client.post("/add_task", json=task)
    assert response.status_code == 201
    assert "Task created" in response.json["message"]

def test_duplicate_task_id(client):
    task = {
        "ID": 101,
        "title": "Duplicate Task",
        "description": "Duplicate",
        "due_date": "2099-12-31",
        "status": "Pending"
    }
    response = client.post("/add_task", json=task)
    assert response.status_code == 409
    assert "Duplicate ID" in response.json["error"]

def test_create_task_invalid_status(client):
    task = {
        "ID": 103,
        "title": "Invalid Status",
        "description": "Wrong status",
        "due_date": "2099-12-31",
        "status": "Started"
    }
    response = client.post("/add_task", json=task)
    assert response.status_code == 400
    assert "Invalid status type" in response.json["error"]

def test_create_task_empty_title(client):
    task = {
        "ID": 104,
        "title": "",
        "description": "Empty title",
        "due_date": "2099-12-31",
        "status": "Pending"
    }
    response = client.post("/add_task", json=task)
    assert response.status_code == 400
    assert "Title cannot be empty" in response.json["error"]
def test_create_task_due_date_string(client):
    task = {
        "ID": 202,
        "title": "Invalid date string",
        "description": "Bad date",
        "due_date": "abcd",
        "status": "Pending"
    }
    response = client.post("/add_task", json=task)
    assert response.status_code == 400  
                                                    
def test_create_task_back_date_status_pending(client):
    task = {
        "ID": 104,
        "title": "Back due date with status pending",
        "description": "Wrong due date",
        "due_date": "2009-12-31",
        "status": "Pending"
    }
    response = client.post("/add_task", json=task)
    assert response.status_code == 400
   
def test_get_all_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_task_by_id_found(client):
    response = client.get("/tasks/101")
    assert response.status_code == 200
    assert response.json[0]["id"] == 101

def test_get_task_by_id_not_found(client):
    response = client.get("/tasks/9799")
    assert response.status_code == 404
    assert "not found" in response.json["error"].lower()

def test_get_completed_tasks(client):
    response = client.get("/tasks/completed")
    assert response.status_code == 200

def test_get_pending_tasks(client):
    response = client.get("/tasks/pending")
    assert response.status_code == 200

def test_get_overdue_tasks(client):
    response = client.get("/tasks/overdue")
    assert response.status_code == 200

def test_update_task(client):
    task = {
        "ID": 101,
        "title": "Updated Task",
        "description": "Updated desc",
        "due_date": "2099-12-31",
        "status": "Completed"
    }
    response = client.put("/tasks/101", json=task)
    assert response.status_code == 200
    assert "Task updated" in response.json["message"]

def test_update_task_id_mismatch(client):
    task = {
        "ID": 998,
        "title": "Mismatch",
        "description": "Mismatch",
        "due_date": "2099-12-31",
        "status": "Pending"
    }
    response = client.put("/tasks/101", json=task)
    assert response.status_code == 400
    assert "do not match" in response.json["error"]
def test_update_task_invalid_status(client):
    task = {
        "ID": 101,
        "title": "Invalid Status",
        "description": "Error",
        "due_date": "2025-12-01",
        "status": "Started"
    }
    response = client.put("/tasks/101", json=task)
    assert response.status_code == 400
    assert "Invalid status type" in response.json["error"]

def test_update_task_empty_title(client):
    task = {
        "ID": 101,
        "title": "   ",
        "description": "Empty title",
        "due_date": "2025-12-01",
        "status": "Pending"
    }
    response = client.put("/tasks/101", json=task)
    assert response.status_code == 400
    assert "Title cannot be empty" in response.json["error"]

def test_update_task_invalid_due_date_format(client):
    task = {
        "ID": 101,
        "title": "Bad Date",
        "description": "Error",
        "due_date": "01-12-2025",
        "status": "Pending"
    }
    response = client.put("/tasks/101", json=task)
    assert response.status_code == 400
    assert "Invalid due_date format" in response.json["error"]

def test_update_task_past_due_date_auto_overdue(client):
    task = {
        "ID": 101,
        "title": "Past Date",
        "description": "Auto overdue",
        "due_date": "2000-01-01",
        "status": "Pending"
    }
    response = client.put("/tasks/101", json=task)
    assert response.status_code == 200

def test_update_task_not_found(client):
    task = {
        "ID": 9989,
        "title": "Not Found",
        "description": "No task",
        "due_date": "2025-12-01",
        "status": "Pending"
    }
    response = client.put("/tasks/9989", json=task)
    assert response.status_code == 200

def test_delete_task(client):
    response = client.delete("/tasks/101")
    assert response.status_code == 200
    assert "Task deleted" in response.json["message"]

def test_delete_task_not_found(client):
    response = client.delete("/tasks/9889")
    assert response.status_code == 404
    assert "not found" in response.json["error"].lower()