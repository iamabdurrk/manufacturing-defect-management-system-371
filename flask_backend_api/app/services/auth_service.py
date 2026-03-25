"""Authentication service (business rules)."""

from __future__ import annotations

from werkzeug.security import check_password_hash, generate_password_hash

from app.utils.errors import abort_json
from app.utils.jwt import create_access_token



class AuthService:
    """Handles signup/login workflows."""

    def __init__(self, *, users_repo, settings):
        self._users = users_repo
        self._settings = settings

    def signup(self, payload: dict) -> dict:
        existing = self._users.find_by_email(payload["email"].lower())
        if existing:
            abort_json(422, "Email already in use")

        user_doc = {
            "name": payload["name"].strip(),
            "email": payload["email"].lower(),
            "password_hash": generate_password_hash(payload["password"]),
            "role": payload["role"],
        }
        user_id = self._users.insert(user_doc)
        user_doc["_id"] = user_id  # temporary for response shaping

        token = create_access_token(
            secret=self._settings.jwt_secret,
            user_id=user_id,
            email=user_doc["email"],
            name=user_doc["name"],
            role=user_doc["role"],
            issuer=self._settings.jwt_issuer,
            audience=self._settings.jwt_audience,
            exp_minutes=self._settings.jwt_exp_minutes,
        )
        user_resp = {"id": user_id, "name": user_doc["name"], "email": user_doc["email"], "role": user_doc["role"]}
        return {"token": token, "user": user_resp}

    def login(self, payload: dict) -> dict:
        user = self._users.find_by_email(payload["email"].lower())
        if not user or not check_password_hash(user.get("password_hash", ""), payload["password"]):
            abort_json(401, "Invalid email or password")

        user_id = str(user["_id"])
        token = create_access_token(
            secret=self._settings.jwt_secret,
            user_id=user_id,
            email=user["email"],
            name=user["name"],
            role=user["role"],
            issuer=self._settings.jwt_issuer,
            audience=self._settings.jwt_audience,
            exp_minutes=self._settings.jwt_exp_minutes,
        )
        user_resp = {"id": user_id, "name": user["name"], "email": user["email"], "role": user["role"]}
        return {"token": token, "user": user_resp}
