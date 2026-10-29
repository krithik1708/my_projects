from fastapi.testclient import TestClient
from main import app
from uuid import uuid4

client= TestClient(app)

def test_app_responds():
    response= client.get("/docs")

    assert response.status_code == 200

def test_register_success():
    username = f"test_{uuid4().hex[:12]}"
    response= client.post(
        "/register",
        json= {
            "username": username,
            "password": "Test123",
            "role": "user"
        }
    )
    assert response.status_code == 200

def test_register_duplicate_user():
    user_data= {
        "username": f"duplicate_{uuid4().hex[:8]}",
        "password": "Abc123",
        "role": "user"
    }
    response1 = client.post(
        "/register",
        json= user_data
    )
    assert response1.status_code == 200
    response2 = client.post(
        "/register",
        json=user_data,
    )
    assert response2.status_code == 409



