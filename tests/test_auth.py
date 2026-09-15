import pytest

from server.app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret-key-that-is-at-least-32-bytes-long"

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()

def test_signup(client):
    response = client.post(
        "/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret123"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "User created successfully"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"
    assert "access_token" in data

def test_login(client):
    client.post(
        "/signup",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "secret123"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "loginuser",
            "password": "secret123"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Login successful"
    assert data["user"]["username"] == "loginuser"
    assert "access_token" in data

def test_me(client):
    client.post(
        "/signup",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": "secret123"
        }
    )

    login_response = client.post(
        "/login",
        json={
            "username": "meuser",
            "password": "secret123"
        }
    )

    token = login_response.get_json()["access_token"]

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["user"]["username"] == "meuser"
    assert data["user"]["email"] == "me@example.com"

def test_signup_missing_fields(client):
    response = client.post(
        "/signup",
        json={
            "username": "incomplete"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "errors" in data
    assert "email" in data["errors"]
    assert "password" in data["errors"]


def test_duplicate_username(client):
    client.post(
        "/signup",
        json={
            "username": "duplicateuser",
            "email": "first@example.com",
            "password": "secret123"
        }
    )

    response = client.post(
        "/signup",
        json={
            "username": "duplicateuser",
            "email": "second@example.com",
            "password": "secret123"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Username already exists"


def test_duplicate_email(client):
    client.post(
        "/signup",
        json={
            "username": "firstuser",
            "email": "same@example.com",
            "password": "secret123"
        }
    )

    response = client.post(
        "/signup",
        json={
            "username": "seconduser",
            "email": "same@example.com",
            "password": "secret123"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Email already exists"


def test_invalid_login(client):
    client.post(
        "/signup",
        json={
            "username": "validuser",
            "email": "valid@example.com",
            "password": "secret123"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "validuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Invalid username or password"

def test_login_missing_fields(client):
    response = client.post(
        "/login",
        json={
            "username": "someuser"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "error" in data


def test_login_missing_body(client):
    response = client.post(
        "/login"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "error" in data