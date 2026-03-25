from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pymongo.collection import Collection

from app.db.mongo import get_db


class CorrectiveActionsRepository:
    def __init__(self) -> None:
        self._col: Collection = get_db()["corrective_actions"]

    def insert(self, doc: dict[str, Any]) -> dict:
        now = datetime.now(timezone.utc)
        doc = {**doc, "created_at": now, "updated_at": now}
        res = self._col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    def find_by_id(self, _id) -> Optional[dict]:
        return self._col.find_one({"_id": _id})

    def update_fields(self, _id, fields: dict[str, Any]) -> Optional[dict]:
        fields = {**fields, "updated_at": datetime.now(timezone.utc)}
        res = self._col.update_one({"_id": _id}, {"$set": fields})
        if res.matched_count == 0:
            return None
        return self.find_by_id(_id)

    def list_by_defect(self, defect_id) -> list[dict]:
        return list(self._col.find({"defect_id": defect_id}).sort("due_date", 1))

    def list_overdue(self, today_iso: str) -> list[dict]:
        # due_date stored as ISO date string; simple comparison works for YYYY-MM-DD or full ISO.
        return list(
            self._col.find({"status": {"$ne": "Complete"}, "due_date": {"$lt": today_iso}}).sort("due_date", 1)
        )
