from fastapi import status


def test_create_song(client, auth_header):
    payload = {
        "title": "Amazing Grace",
        "original_key": "G",
        "playing_key": "A",
        "bpm": 80,
        "notes": "Practice the intro and chorus."
    }
    response = client.post("/songs/", headers=auth_header, json=payload)
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in data
    assert data["title"] == "Amazing Grace"
    assert data["original_key"] == "G"
    assert data["playing_key"] == "A"
    assert data["bpm"] == 80
    assert data["notes"] == "Practice the intro and chorus."


def test_create_song_defaults_playing_key(client, auth_header):
    payload = {
        "title": "Amazing Grace",
        "original_key": "G",
        "bpm": 80,
        "notes": "Practice the intro and chorus."
    }
    response = client.post("/songs/", headers=auth_header, json=payload)
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in data
    assert data["title"] == "Amazing Grace"
    assert data["original_key"] == "G"
    assert data["playing_key"] == "G"
    assert data["bpm"] == 80
    assert data["notes"] == "Practice the intro and chorus."


def test_get_songs(client, auth_header):
    songs = [
        {
            "title": "Amazing Grace",
            "original_key": "G",
            "playing_key": "A",
            "bpm": 80,
            "notes": "Practice the intro."
        },
        {
            "title": "How Great Thou Art",
            "original_key": "D",
            "bpm": 75,
            "notes": "Practice the chorus."
        },
        {
            "title": "Blessed Assurance",
            "original_key": "C",
            "playing_key": "G",
            "bpm": 90,
            "notes": None
        }
    ]
    for song in songs:
        response = client.post("/songs/", headers=auth_header, json=song)
        assert response.status_code == status.HTTP_201_CREATED
    
    response = client.get("/songs/", headers=auth_header)
    data = response.json()
    assert type(data) is list
    assert len(data) == 3
    assert data[0]["title"] == "Amazing Grace"
    assert data[1]["title"] == "How Great Thou Art"
    assert data[2]["title"] == "Blessed Assurance"

    assert data[0]["original_key"] == "G"
    assert data[1]["original_key"] == "D"
    assert data[2]["original_key"] == "C"


def test_get_song_by_id(client, auth_header, song):
    id = song.json()["id"]
    response = client.get(f"/songs/{id}", headers=auth_header)
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == id
    assert data["title"] == "Amazing Grace"
    assert data["original_key"] == "G"
    assert data["playing_key"] == "A"
    assert data["bpm"] == 80
    assert data["notes"] == "Practice the intro and chorus."


def test_get_song_not_found(client, auth_header):
    response = client.get("/songs/1", headers=auth_header)
    data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Song with id 1 not found"
    

def test_update_song(client, auth_header, song):
    id = song.json()["id"]
    payload = {
        "playing_key": "G",
        "bpm": 85,
    }
    response = client.patch(f"/songs/{id}", headers=auth_header, json=payload)   
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["playing_key"] == "G"
    assert data["bpm"] == 85


def test_update_song_not_found(client, auth_header):
    payload = {
        "playing_key": "G",
        "bpm": 85,
    }
    response = client.patch("/songs/1", headers=auth_header, json=payload)
    data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "Song with id 1 not found"


def test_delete_song(client, auth_header, song):
    id = song.json()["id"]
    response = client.delete(f"/songs/{id}", headers=auth_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    

def test_delete_song_not_found(client, auth_header):
    response = client.delete("/songs/1", headers=auth_header)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    

def test_user_cannot_access_another_users_song(client, song):
    id = song.json()["id"]
    register_payload = {
        "username": "john",
        "email": "john@gmail.com",
        "password": "secret123"
    }
    register_user = client.post("/users/register", json=register_payload)
    assert register_user.status_code == status.HTTP_201_CREATED
    
    login_payload = {
        "email": "john@gmail.com",
        "password": "secret123"
    }
    login_response = client.post("/users/login", json=login_payload)
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()['access_token']
    header = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/songs/{id}", headers=header)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Song with id {id} not found"


def test_user_cannot_delete_another_users_song(client, song, auth_header):
    id = song.json()["id"]
    register_payload = {
        "username": "john",
        "email": "john@gmail.com",
        "password": "secret123"
    }
    register_user = client.post("/users/register", json=register_payload)
    assert register_user.status_code == status.HTTP_201_CREATED
    
    login_payload = {
        "email": "john@gmail.com",
        "password": "secret123"
    }
    login_response = client.post("/users/login", json=login_payload)
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()['access_token']
    header = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(f"/songs/{id}", headers=header)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Song with id {id} not found"
    
    response = client.get(f"/songs/{id}", headers=auth_header)
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == id