"""MongoDB repository for root cause analysis (RCA)."""

from __future__ import annotations

from typing import Any

from pymongo.database import Database


class RcaRepository:
    """Data access for rca collection."""

    def __init__(self, db: Database):
        self._col = db.rca

    def find_by_defect_id(self, defect_id) -> dict[str, Any] | None:
        return self._col.find_one({"defect_id": defect_id})

    def upsert(self, doc: dict[str, Any]) -> dict[str, Any]:
        self._col.update_one({"defect_id": doc["defect_id"]}, {"$set": doc}, upsert=True)
        return self._col.find_one({"defect_id": doc["defect_id"]})
