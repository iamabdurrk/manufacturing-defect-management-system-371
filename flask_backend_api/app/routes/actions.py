"""Corrective actions routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.schemas.defects import CorrectiveActionCreateSchema, CorrectiveActionUpdateSchema
from app.utils.errors import abort_json
from app.utils.jwt import jwt_required

bp = Blueprint("actions", __name__, url_prefix="/api/actions")


@bp.get("")
def list_actions():
    """List corrective actions (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    svc = request.app_ctx["services"]["actions"]
    return jsonify(svc.list_actions())


@bp.post("")
def create_action():
    """Create corrective action (JWT required, with RCA gating in service)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    data = request.get_json(silent=True) or {}
    schema = CorrectiveActionCreateSchema()
    errors = schema.validate(data)
    if errors:
        abort_json(422, "Validation error", errors=errors)

    svc = request.app_ctx["services"]["actions"]
    created = svc.create_action(schema.load(data), created_by=request.app_ctx["current_user"]())
    return jsonify(created)


@bp.put("/<action_id>")
def update_action(action_id: str):
    """Update corrective action (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    data = request.get_json(silent=True) or {}
    schema = CorrectiveActionUpdateSchema()
    errors = schema.validate(data)
    if errors:
        abort_json(422, "Validation error", errors=errors)

    svc = request.app_ctx["services"]["actions"]
    updated = svc.update_action(action_id, schema.load(data))
    return jsonify(updated)
