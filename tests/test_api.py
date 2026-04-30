"""Core API tests for matchmaker backend."""
import pytest


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def test_register_success(client):
    r = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "test123",
        "nickname": "Newbie",
        "gender": 1,
        "birth_date": "1990-01-01"
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["user"]["email"] == "new@example.com"


def test_register_duplicate_email(client):
    payload = {
        "email": "dup@example.com",
        "password": "test123",
        "nickname": "Dup",
        "gender": 1,
        "birth_date": "1990-01-01"
    }
    assert client.post("/api/auth/register", json=payload).status_code == 200
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 400
    assert "already registered" in r.json()["detail"]


def test_login_success(client):
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "test123",
        "nickname": "Login",
        "gender": 1,
        "birth_date": "1990-01-01"
    })
    r = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "test123"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "password": "test123",
        "nickname": "Wrong",
        "gender": 1,
        "birth_date": "1990-01-01"
    })
    r = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "badpass"
    })
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
def test_get_me(client, auth_headers):
    r = client.get("/api/v1/users/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"


def test_get_me_unauthorized(client):
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401


def test_update_me(client, auth_headers):
    r = client.put("/api/v1/users/me", json={
        "nickname": "Updated",
        "bio": "Hello world"
    }, headers=auth_headers)
    assert r.status_code == 200

    r = client.get("/api/v1/users/me", headers=auth_headers)
    assert r.json()["nickname"] == "Updated"


def test_discover(client, auth_headers, user_b):
    r = client.get("/api/v1/users/discover", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "users" in data
    # user_b (gender=2) should appear in discover for user_a (gender=1)
    assert any(u["nickname"] == "UserB" for u in data["users"])


# ---------------------------------------------------------------------------
# Matches
# ---------------------------------------------------------------------------
def test_like_user(client, auth_headers, user_b):
    # user_a likes user_b (user_b is the second registered user => id=2)
    r = client.post("/api/v1/matches/like", json={"to_user_id": 2}, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["matched"] is False
    assert data["match_id"] is not None


def test_mutual_match_creates_chat(client, auth_headers, user_b):
    # A likes B
    client.post("/api/v1/matches/like", json={"to_user_id": 2}, headers=auth_headers)
    # B likes A
    r = client.post("/api/v1/matches/like", json={"to_user_id": 1}, headers=user_b)
    assert r.status_code == 200
    assert r.json()["matched"] is True

    # Chat should be created
    r = client.get("/api/chat/conversations", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()["conversations"]) == 1


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
def test_send_and_get_messages(client, auth_headers, user_b):
    # Create mutual match => chat created
    client.post("/api/v1/matches/like", json={"to_user_id": 2}, headers=auth_headers)
    client.post("/api/v1/matches/like", json={"to_user_id": 1}, headers=user_b)

    # Get conversations
    r = client.get("/api/chat/conversations", headers=auth_headers)
    chat_id = r.json()["conversations"][0]["id"]

    # Send message
    r = client.post("/api/chat/messages", json={
        "chat_id": chat_id,
        "content": "Hello from test!"
    }, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["content"] == "Hello from test!"

    # Get messages
    r = client.get(f"/api/chat/messages/{chat_id}", headers=auth_headers)
    assert r.status_code == 200
    msgs = r.json()["messages"]
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Hello from test!"


def test_conversations_empty(client, auth_headers):
    r = client.get("/api/chat/conversations", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["conversations"] == []
