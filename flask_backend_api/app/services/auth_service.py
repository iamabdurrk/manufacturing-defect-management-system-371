from __future__ import annotations

from app.repositories.users_repo import UsersRepository
from app.utils.errors import ConflictError, UnauthorizedError
from app.utils.jwt_utils import create_access_token
from app.utils.passwords import hash_password, verify_password
from app.utils.serialization import serialize_doc


class AuthService:
    """Auth service: signup/login and JWT issuance."""

    def __init__(self) -> None:
        self._users = UsersRepository()

    def signup(self, name: str, email: str, password: str, role: str) -> dict:
        existing = self._users.find_by_email(email)
        if existing:
            raise ConflictError("Email already registered")

        user = self._users.insert_user(name=name, email=email, password_hash=hash_password(password), role=role)
        token = create_access_token(user_id=str(user["_id"]), email=user["email"], role=user["role"])
        user_safe = {k: v for k, v in user.items() if k != "password_hash"}
        return {"token": token, "user": serialize_doc(user_safe)}

    def login(self, email: str, password: str) -> dict:
        user = self._users.find_by_email(email)
        if not user or not verify_password(password, user.get("password_hash", "")):
            raise UnauthorizedError("Invalid email or password")

        token = create_access_token(user_id=str(user["_id"]), email=user["email"], role=user["role"])
        user_safe = {k: v for k, v in user.items() if k != "password_hash"}
        return {"token": token, "user": serialize_doc(user_safe)}
