"""Analytics routes: pareto and trends."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.utils.errors import abort_json
from app.utils.jwt import jwt_required

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@bp.get("/pareto")
def pareto():
    """Pareto chart data (JWT required). Query params: start, end."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    start = request.args.get("start")
    end = request.args.get("end")
    svc = request.app_ctx["services"]["analytics"]
    try:
        return jsonify(svc.pareto(start, end))
    except Exception as e:
        # Most parsing errors are due to invalid dates
        abort_json(422, "Invalid parameters", errors={"detail": str(e)})


@bp.get("/trends")
def trends():
    """Trend series data (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    params = {
        "start": request.args.get("start"),
        "end": request.args.get("end"),
        "interval": request.args.get("interval"),
        "production_line": request.args.get("production_line"),
        "part_number": request.args.get("part_number"),
        "defect_type_id": request.args.get("defect_type_id"),
    }
    svc = request.app_ctx["services"]["analytics"]
    return jsonify(
        svc.trends(
            start=params["start"],
            end=params["end"],
            interval=params["interval"],
            production_line=params["production_line"],
            part_number=params["part_number"],
            defect_type_id=params["defect_type_id"],
        )
    )
