from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pymongo.collection import Collection

from app.db.mongo import get_db


class UsersRepository:
    """MongoDB access for users collection."""

    def __init__(self) -> None:
        self._col: Collection = get_db()["users"]

    def find_by_email(self, email: str) -> Optional[dict]:
        return self._col.find_one({"email": email.lower().strip()})

    def find_by_id(self, user_id) -> Optional[dict]:
        return self._col.find_one({"_id": user_id})

    def insert_user(self, name: str, email: str, password_hash: str, role: str) -> dict:
        doc = {
            "name": name,
            "email": email.lower().strip(),
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.now(timezone.utc),
        }
        res = self._col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc
