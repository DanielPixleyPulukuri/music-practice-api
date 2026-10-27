from fastapi import status


def test_create_practice_session(client, auth_header, song):
    payload = {
        "song_id": song.json()["id"],
        "practiced_at": "2026-01-15T18:30:00",
        "duration_minutes": 30,
        "notes": "Practiced the intro and chorus."
    }

    response = client.post(
        "/practice-sessions/",
        headers=auth_header,
        json=payload
    )

    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in data
    assert data["song_id"] == payload["song_id"]
    assert data["duration_minutes"] == 30
    assert data["notes"] == "Practiced the intro and chorus."


def test_create_practice_session_for_nonexistent_song(client, auth_header):
    payload = {
        "song_id": 9999,
        "practiced_at": "2026-01-15T18:30:00",
        "duration_minutes": 30,
        "notes": "Practice session for a nonexistent song."
    }

    response = client.post(
        "/practice-sessions/",
        headers=auth_header,
        json=payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_practice_sessions(client, auth_header, practice_session):
    response = client.get(
        "/practice-sessions/",
        headers=auth_header
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == practice_session["id"]


def test_get_practice_session_by_id(client, auth_header, practice_session):
    practice_session_id = practice_session["id"]

    response = client.get(
        f"/practice-sessions/{practice_session_id}",
        headers=auth_header
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == practice_session_id
    assert data["song_id"] == practice_session["song_id"]
    assert data["duration_minutes"] == 30


def test_get_practice_session_not_found(client, auth_header):
    response = client.get(
        "/practice-sessions/9999",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_practice_session(client, auth_header, practice_session):
    session_id = practice_session["id"]

    payload = {
        "duration_minutes": 45,
        "notes": "Practiced the intro, chorus, and ending."
    }

    response = client.patch(
        f"/practice-sessions/{session_id}",
        headers=auth_header,
        json=payload
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == session_id
    assert data["duration_minutes"] == 45
    assert data["notes"] == "Practiced the intro, chorus, and ending."


def test_update_practice_session_not_found(client, auth_header):
    payload = {"duration_minutes": 45}

    response = client.patch(
        "/practice-sessions/9999",
        headers=auth_header,
        json=payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_practice_session(client, auth_header, practice_session):
    session_id = practice_session["id"]

    response = client.delete(
        f"/practice-sessions/{session_id}",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(
        f"/practice-sessions/{session_id}",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_practice_session_not_found(client, auth_header):
    response = client.delete(
        "/practice-sessions/9999",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthenticated_user_cannot_access_practice_sessions(client):
    response = client.get("/practice-sessions/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_cannot_access_another_users_practice_session(
    client, auth_header, practice_session
):
    session_id = practice_session["id"]

    register_payload = {
        "username": "john",
        "email": "john@gmail.com",
        "password": "secret123"
    }

    register_response = client.post(
        "/users/register",
        json=register_payload
    )

    assert register_response.status_code == status.HTTP_201_CREATED

    login_response = client.post(
        "/users/login",
        json={
            "email": "john@gmail.com",
            "password": "secret123"
        }
    )

    assert login_response.status_code == status.HTTP_200_OK

    token = login_response.json()["access_token"]
    john_header = {"Authorization": f"Bearer {token}"}

    response = client.get(
        f"/practice-sessions/{session_id}",
        headers=john_header
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # The original owner can still access the session.
    response = client.get(
        f"/practice-sessions/{session_id}",
        headers=auth_header
    )

    assert response.status_code == status.HTTP_200_OK