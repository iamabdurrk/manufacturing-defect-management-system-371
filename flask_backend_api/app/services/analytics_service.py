"""Analytics service: pareto and trends aggregates."""

from __future__ import annotations



from app.utils.errors import abort_json
from app.utils.serialization import parse_date


class AnalyticsService:
    """Computes dashboard aggregates from defects."""

    def __init__(self, *, db):
        self._defects = db.defects

    def pareto(self, start: str | None, end: str | None) -> dict:
        match = {}
        if start:
            match.setdefault("created_at_dt", {})
            match["created_at_dt"]["$gte"] = parse_date(start)
        if end:
            match.setdefault("created_at_dt", {})
            match["created_at_dt"]["$lte"] = parse_date(end)

        pipeline = []
        if match:
            pipeline.append({"$match": match})
        pipeline.extend(
            [
                {"$group": {"_id": "$defect_type_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
        )
        rows = list(self._defects.aggregate(pipeline))
        total = sum(r["count"] for r in rows) or 0
        cumulative = 0
        out = []
        for r in rows:
            cumulative += r["count"]
            pct = (r["count"] / total) * 100 if total else 0
            cum_pct = (cumulative / total) * 100 if total else 0
            out.append(
                {
                    "defect_type_id": r["_id"],
                    "count": r["count"],
                    "percent": round(pct, 2),
                    "cumulative_percent": round(cum_pct, 2),
                }
            )
        return {"total": total, "items": out}

    def trends(
        self,
        start: str | None,
        end: str | None,
        interval: str | None,
        production_line: str | None,
        part_number: str | None,
        defect_type_id: str | None,
    ) -> dict:
        # Supported intervals: day, week, month (default: day)
        interval = (interval or "day").lower()
        if interval not in ["day", "week", "month"]:
            abort_json(422, "Invalid interval", errors={"interval": "Use day|week|month"})

        match = {}
        if start:
            match.setdefault("created_at_dt", {})
            match["created_at_dt"]["$gte"] = parse_date(start)
        if end:
            match.setdefault("created_at_dt", {})
            match["created_at_dt"]["$lte"] = parse_date(end)
        if production_line:
            match["production_line"] = production_line
        if part_number:
            match["part_number"] = part_number
        if defect_type_id:
            match["defect_type_id"] = defect_type_id

        if interval == "day":
            fmt = "%Y-%m-%d"
        elif interval == "week":
            fmt = "%G-W%V"
        else:
            fmt = "%Y-%m"

        pipeline = []
        if match:
            pipeline.append({"$match": match})
        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": {"$dateToString": {"format": fmt, "date": "$created_at_dt"}},
                        "count": {"$sum": 1},
                    }
                },
                {"$sort": {"_id": 1}},
            ]
        )
        rows = list(self._defects.aggregate(pipeline))
        return {"interval": interval, "items": [{"bucket": r["_id"], "count": r["count"]} for r in rows]}
