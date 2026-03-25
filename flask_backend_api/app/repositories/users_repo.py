"""MongoDB repository for users."""

from __future__ import annotations

from typing import Any

from pymongo.database import Database


class UsersRepository:
    """Data access for users collection."""

    def __init__(self, db: Database):
        self._col = db.users

    def find_by_email(self, email: str) -> dict[str, Any] | None:
        return self._col.find_one({"email": email})

    def insert(self, user: dict[str, Any]) -> str:
        res = self._col.insert_one(user)
        return str(res.inserted_id)

    def find_by_id(self, user_id) -> dict[str, Any] | None:
        return self._col.find_one({"_id": user_id})
