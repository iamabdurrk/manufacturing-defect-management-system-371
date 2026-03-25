from __future__ import annotations

from datetime import datetime, timezone

from pymongo.collection import Collection

from app.db.mongo import get_db


class SeverityRulesRepository:
    def __init__(self) -> None:
        self._col: Collection = get_db()["severity_rules"]

    def list(self) -> list[dict]:
        return list(self._col.find({}).sort("name", 1))

    def upsert(self, name: str, condition: dict, severity: str) -> dict:
        now = datetime.now(timezone.utc)
        self._col.update_one(
            {"name": name},
            {"$set": {"condition": condition, "severity": severity, "updated_at": now}, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        return self._col.find_one({"name": name})  # type: ignore[return-value]
