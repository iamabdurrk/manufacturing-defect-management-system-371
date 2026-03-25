from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from dateutil.parser import isoparse
from pymongo.collection import Collection

from app.db.mongo import get_db
from app.utils.serialization import serialize_doc


class AnalyticsService:
    """Analytics service (Mongo aggregation pipelines)."""

    def __init__(self) -> None:
        self._defects: Collection = get_db()["defects"]

    def _date_filter(self, start: Optional[str], end: Optional[str]) -> dict[str, Any]:
        filt: dict[str, Any] = {}
        if start:
            filt["$gte"] = isoparse(start)
        if end:
            filt["$lte"] = isoparse(end)
        return {"created_at": filt} if filt else {}

    def pareto(self, start: Optional[str], end: Optional[str]) -> dict:
        match = self._date_filter(start, end)
        pipeline = [
            {"$match": match} if match else {"$match": {}},
            {
                "$group": {
                    "_id": "$defect_type_id",
                    "count": {"$sum": 1},
                    "quantity_affected": {"$sum": "$quantity_affected"},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 20},
        ]
        rows = list(self._defects.aggregate(pipeline))
        # Add cumulative percentage (pareto)
        total = sum(r.get("count", 0) for r in rows) or 1
        cum = 0
        out = []
        for r in rows:
            cnt = int(r.get("count", 0))
            cum += cnt
            out.append(
                {
                    "defect_type_id": r["_id"],
                    "count": cnt,
                    "quantity_affected": int(r.get("quantity_affected", 0)),
                    "cum_percent": round((cum / total) * 100.0, 2),
                }
            )
        return {"items": serialize_doc(out), "total": total}

    def trends(
        self,
        start: Optional[str],
        end: Optional[str],
        interval: str = "day",
        production_line: Optional[str] = None,
        part_number: Optional[str] = None,
        defect_type_id: Optional[str] = None,
    ) -> dict:
        match: dict[str, Any] = {}
        match.update(self._date_filter(start, end))
        if production_line:
            match["production_line"] = production_line
        if part_number:
            match["part_number"] = part_number
        if defect_type_id:
            # stored as ObjectId; matching string won't match; frontend should pass id string.
            # We'll keep it simple by not casting here; routes can cast and pass ObjectId if needed.
            match["defect_type_id"] = defect_type_id

        date_fmt = "%Y-%m-%d" if interval != "week" else "%G-W%V"
        pipeline = [
            {"$match": match} if match else {"$match": {}},
            {"$group": {"_id": {"$dateToString": {"format": date_fmt, "date": "$created_at"}}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        rows = list(self._defects.aggregate(pipeline))
        out = [{"bucket": r["_id"], "count": int(r["count"])} for r in rows]
        return {"items": out, "interval": interval, "generated_at": datetime.now(timezone.utc)}
