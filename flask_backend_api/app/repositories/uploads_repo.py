from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pymongo.collection import Collection

from app.db.mongo import get_db


class UploadsRepository:
    def __init__(self) -> None:
        self._col: Collection = get_db()["uploads"]

    def insert(self, filename: str, content_type: str, size: int, path: str) -> dict:
        doc = {
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "path": path,
            "created_at": datetime.now(timezone.utc),
        }
        res = self._col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    def find_by_id(self, _id) -> Optional[dict]:
        return self._col.find_one({"_id": _id})
