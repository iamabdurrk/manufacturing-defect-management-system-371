from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pymongo.collection import Collection

from app.db.mongo import get_db


class RootCausesRepository:
    """MongoDB access for root_causes and why_analysis collections."""

    def __init__(self) -> None:
        self._col: Collection = get_db()["root_causes"]
        self._why: Collection = get_db()["why_analysis"]

    def get_root_cause(self, defect_id) -> Optional[dict]:
        return self._col.find_one({"defect_id": defect_id})

    def upsert_root_cause(self, defect_id, method: str, created_by) -> dict:
        now = datetime.now(timezone.utc)
        self._col.update_one(
            {"defect_id": defect_id},
            {"$set": {"method": method, "updated_at": now}, "$setOnInsert": {"created_at": now, "created_by": created_by}},
            upsert=True,
        )
        return self._col.find_one({"defect_id": defect_id})  # type: ignore[return-value]

    def replace_five_whys(self, defect_id, root_cause_id, whys: list[str]) -> None:
        self._why.delete_many({"defect_id": defect_id})
        now = datetime.now(timezone.utc)
        docs = [
            {
                "defect_id": defect_id,
                "root_cause_id": root_cause_id,
                "why_level": i + 1,
                "description": w,
                "created_at": now,
            }
            for i, w in enumerate(whys)
        ]
        if docs:
            self._why.insert_many(docs)

    def list_five_whys(self, defect_id) -> list[dict]:
        return list(self._why.find({"defect_id": defect_id}).sort("why_level", 1))
