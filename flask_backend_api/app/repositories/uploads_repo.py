"""MongoDB repository for uploaded file metadata."""

from __future__ import annotations

from typing import Any

from pymongo.database import Database


class UploadsRepository:
    """Data access for uploads collection."""

    def __init__(self, db: Database):
        self._col = db.uploads

    def insert(self, doc: dict[str, Any]) -> str:
        res = self._col.insert_one(doc)
        return str(res.inserted_id)

    def find_by_id(self, _id) -> dict[str, Any] | None:
        return self._col.find_one({"_id": _id})
