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


@pytest.fixture
def auth_headers(client):
    client.post(
        "/signup",
        json={
            "username": "noteuser",
            "email": "note@example.com",
            "password": "secret123"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "noteuser",
            "password": "secret123"
        }
    )

    token = response.get_json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

def test_create_note(client, auth_headers):
    response = client.post(
        "/notes",
        json={
            "title": "Test Note",
            "content": "This is a test note."
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Note created successfully"
    assert data["note"]["title"] == "Test Note"
    assert data["note"]["content"] == "This is a test note."
    assert "id" in data["note"]
    assert "user_id" in data["note"]

def test_get_notes_with_pagination(client, auth_headers):
    for i in range(6):
        client.post(
            "/notes",
            json={
                "title": f"Note {i + 1}",
                "content": f"Content {i + 1}"
            },
            headers=auth_headers
        )

    response = client.get(
        "/notes?page=1&per_page=3",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["notes"]) == 3
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 3
    assert data["pagination"]["total"] == 6
    assert data["pagination"]["pages"] == 2
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_prev"] is False

def test_get_single_note(client, auth_headers):
    create_response = client.post(
        "/notes",
        json={
            "title": "Single Note",
            "content": "Testing a single note."
        },
        headers=auth_headers
    )

    note_id = create_response.get_json()["note"]["id"]

    response = client.get(
        f"/notes/{note_id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["note"]["id"] == note_id
    assert data["note"]["title"] == "Single Note"
    assert data["note"]["content"] == "Testing a single note."

def test_user_isolation(client, auth_headers):
    # Create a note as User 1
    create_response = client.post(
        "/notes",
        json={
            "title": "Private Note",
            "content": "This belongs to User 1."
        },
        headers=auth_headers
    )

    note_id = create_response.get_json()["note"]["id"]

    # Create User 2
    client.post(
        "/signup",
        json={
            "username": "seconduser",
            "email": "second@example.com",
            "password": "secret123"
        }
    )

    login_response = client.post(
        "/login",
        json={
            "username": "seconduser",
            "password": "secret123"
        }
    )

    second_token = login_response.get_json()["access_token"]

    second_headers = {
        "Authorization": f"Bearer {second_token}"
    }

    # User 2 tries to access User 1's note
    response = client.get(
        f"/notes/{note_id}",
        headers=second_headers
    )

    assert response.status_code == 404

def test_update_note(client, auth_headers):
    create_response = client.post(
        "/notes",
        json={
            "title": "Original Title",
            "content": "Original content."
        },
        headers=auth_headers
    )

    note_id = create_response.get_json()["note"]["id"]

    response = client.patch(
        f"/notes/{note_id}",
        json={
            "title": "Updated Title",
            "content": "Updated content."
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Note updated successfully"
    assert data["note"]["id"] == note_id
    assert data["note"]["title"] == "Updated Title"
    assert data["note"]["content"] == "Updated content."

def test_delete_note(client, auth_headers):
    create_response = client.post(
        "/notes",
        json={
            "title": "Delete Me",
            "content": "This note should be deleted."
        },
        headers=auth_headers
    )

    note_id = create_response.get_json()["note"]["id"]

    response = client.delete(
        f"/notes/{note_id}",
        headers=auth_headers
    )

    assert response.status_code == 204
    assert response.data == b""

    # Confirm the note no longer exists
    get_response = client.get(
        f"/notes/{note_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 404

def test_notes_require_authentication(client):
    # GET all notes
    response = client.get("/notes")
    assert response.status_code == 401

    # GET one note
    response = client.get("/notes/1")
    assert response.status_code == 401

    # POST a note
    response = client.post(
        "/notes",
        json={
            "title": "Unauthorized",
            "content": "This should not be created."
        }
    )
    assert response.status_code == 401

    # PATCH a note
    response = client.patch(
        "/notes/1",
        json={
            "title": "Unauthorized update"
        }
    )
    assert response.status_code == 401

    # DELETE a note
    response = client.delete("/notes/1")
    assert response.status_code == 401

def test_create_note_validation(client, auth_headers):
    # Empty title
    response = client.post(
        "/notes",
        json={
            "title": "",
            "content": "Valid content."
        },
        headers=auth_headers
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "errors" in data
    assert "title" in data["errors"]


def test_update_note_validation(client, auth_headers):
    # Create a valid note first
    create_response = client.post(
        "/notes",
        json={
            "title": "Valid Note",
            "content": "Valid content."
        },
        headers=auth_headers
    )

    note_id = create_response.get_json()["note"]["id"]

    # Try to update with an empty title
    response = client.patch(
        f"/notes/{note_id}",
        json={
            "title": ""
        },
        headers=auth_headers
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "errors" in data
    assert "title" in data["errors"]

def test_create_note_missing_body(client, auth_headers):
    response = client.post(
        "/notes",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_update_note_missing_body(client, auth_headers):
    create_response = client.post(
        "/notes",
        json={
            "title": "Valid Note",
            "content": "Valid content."
        },
        headers=auth_headers
    )

    note_id = create_response.get_json()["note"]["id"]

    response = client.patch(
        f"/notes/{note_id}",
        headers=auth_headers
    )

    assert response.status_code == 400
