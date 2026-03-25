"""MongoDB repository for defects."""

from __future__ import annotations

from typing import Any

from pymongo.database import Database


class DefectsRepository:
    """Data access for defects collection."""

    def __init__(self, db: Database):
        self._col = db.defects

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._col.find({}).sort("created_at", -1))

    def insert(self, doc: dict[str, Any]) -> str:
        res = self._col.insert_one(doc)
        return str(res.inserted_id)

    def find_by_id(self, _id) -> dict[str, Any] | None:
        return self._col.find_one({"_id": _id})

    def update_by_id(self, _id, updates: dict[str, Any]) -> dict[str, Any] | None:
        self._col.update_one({"_id": _id}, {"$set": updates})
        return self.find_by_id(_id)
