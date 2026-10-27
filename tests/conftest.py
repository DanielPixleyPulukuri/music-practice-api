import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import TEST_DATABASE_URL
from app.database import Base, get_db
from app.main import app

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def create_tables():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(create_tables):
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    payload = {
        "username": "daniel",
        "email": "daniel@gmail.com",
        "password": "secret123"
    }
    response = client.post("/users/register", json=payload)
    return response


@pytest.fixture
def auth_header(client, test_user):
    payload = {
        "email": "daniel@gmail.com",
        "password": "secret123"
    }
    response = client.post("/users/login", json=payload)
    token = response.json()['access_token']
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def song(client, auth_header):
    payload = {
        "title": "Amazing Grace",
        "original_key": "G",
        "playing_key": "A",
        "bpm": 80,
        "notes": "Practice the intro and chorus."
    }
    response = client.post("/songs/", headers=auth_header, json=payload)
    return response


@pytest.fixture
def practice_session(client, auth_header, song):
    song_id = song.json()["id"]

    payload = {
        "song_id": song_id,
        "practiced_at": "2026-01-15T18:30:00",
        "duration_minutes": 30,
        "notes": "Practiced the intro and chorus."
    }

    response = client.post(
        "/practice-sessions/",
        headers=auth_header,
        json=payload
    )

    assert response.status_code == 201
    return response.json()