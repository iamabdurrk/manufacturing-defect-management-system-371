from __future__ import annotations

from unittest.mock import patch


def test_signup_success_returns_token_and_user(client):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",
        "role": "quality_engineer",
    }

    with patch("app.routes.auth.AuthService") as AuthService:
        AuthService.return_value.signup.return_value = {
            "token": "jwt-token",
            "user": {"_id": "u1", "name": "Alice", "email": "alice@example.com", "role": "quality_engineer"},
        }

        res = client.post("/api/auth/signup", json=payload)

    assert res.status_code == 200
    data = res.get_json()
    assert "token" in data and data["token"] == "jwt-token"
    assert "user" in data
    assert data["user"]["email"] == "alice@example.com"
    # Ensure password is not leaked by route/response shape (service should exclude it).
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_login_invalid_payload_is_422(client):
    # Missing password/email should be rejected by marshmallow schema.
    res = client.post("/api/auth/login", json={"email": "a@b.com"})
    assert res.status_code == 422
    assert res.is_json


def test_login_success_returns_token_and_user(client):
    payload = {"email": "alice@example.com", "password": "secret123"}
    with patch("app.routes.auth.AuthService") as AuthService:
        AuthService.return_value.login.return_value = {
            "token": "jwt-token",
            "user": {"_id": "u1", "name": "Alice", "email": "alice@example.com", "role": "quality_engineer"},
        }

        res = client.post("/api/auth/login", json=payload)

    assert res.status_code == 200
    data = res.get_json()
    assert data["token"] == "jwt-token"
    assert data["user"]["role"] == "quality_engineer"
