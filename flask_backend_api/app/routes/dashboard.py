"""Dashboard endpoints: overdue actions."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.utils.jwt import jwt_required

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("/overdue-actions")
def overdue_actions():
    """List overdue corrective actions (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    svc = request.app_ctx["services"]["actions"]
    return jsonify(svc.list_overdue())
