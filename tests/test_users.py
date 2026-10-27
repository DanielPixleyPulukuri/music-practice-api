from fastapi import status


def test_register_user(test_user):
    data = test_user.json()

    assert test_user.status_code == status.HTTP_201_CREATED
    assert data["id"] > 0
    assert data["username"] == "daniel"
    assert data["email"] == "daniel@gmail.com"


def test_register_user_duplicate_email(client, test_user):
    payload = {
        "username": "daniel",
        "email": "daniel@gmail.com",
        "password": "secret123",
    }
    response = client.post("/users/register", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Username or email already exists"


def test_register_user_validation_error(client):
    payload = {
        "username": "daniel",
    }
    response = client.post("/users/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_login_success(client, test_user):
    login_payload = {
        "email": "daniel@gmail.com",
        "password": "secret123",
    }
    response = client.post("/users/login", json=login_payload)
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_login_invalid_password(client, test_user):
    login_payload = {
        "email": "daniel@gmail.com",
        "password": "secret12",
    }
    response = client.post("/users/login", json=login_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email or password"


def test_login_user_not_found(client):
    login_payload = {
        "email": "random@gmail.com",
        "password": "secret12",
    }
    response = client.post("/users/login", json=login_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid email or password"


def test_get_current_user(client, test_user):
    login_payload = {
        "email": "daniel@gmail.com",
        "password": "secret123",
    }
    login_data = client.post("/users/login", json=login_payload)
    token = login_data.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["username"] == "daniel"
    assert data["email"] == "daniel@gmail.com"


def test_get_current_user_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"
