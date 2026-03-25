from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult

from app.db.mongo import get_db


class DefectTypesRepository:
    """MongoDB access for defect_types collection."""

    def __init__(self) -> None:
        self._col: Collection = get_db()["defect_types"]

    def list(self) -> list[dict]:
        return list(self._col.find({"is_active": {"$ne": False}}).sort("name", 1))

    def upsert(self, code: str, name: str, description: Optional[str], is_active: bool) -> dict:
        doc = {
            "code": code,
            "name": name,
            "description": description,
            "is_active": is_active,
            "updated_at": datetime.now(timezone.utc),
        }
        self._col.update_one(
            {"code": code},
            {"$set": doc, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        return self._col.find_one({"code": code})  # type: ignore[return-value]

    def find_by_id(self, _id) -> Optional[dict]:
        return self._col.find_one({"_id": _id})


class DefectsRepository:
    """MongoDB access for defects collection."""

    def __init__(self) -> None:
        self._col: Collection = get_db()["defects"]

    def insert(self, doc: dict[str, Any]) -> dict:
        now = datetime.now(timezone.utc)
        doc = {**doc, "created_at": now, "updated_at": now}
        res: InsertOneResult = self._col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    def list(self, filters: dict[str, Any], limit: int, skip: int) -> list[dict]:
        return list(self._col.find(filters).sort("created_at", -1).skip(skip).limit(limit))

    def count(self, filters: dict[str, Any]) -> int:
        return int(self._col.count_documents(filters))

    def find_by_id(self, _id) -> Optional[dict]:
        return self._col.find_one({"_id": _id})

    def update_fields(self, _id, fields: dict[str, Any]) -> Optional[dict]:
        fields = {**fields, "updated_at": datetime.now(timezone.utc)}
        res: UpdateResult = self._col.update_one({"_id": _id}, {"$set": fields})
        if res.matched_count == 0:
            return None
        return self.find_by_id(_id)
