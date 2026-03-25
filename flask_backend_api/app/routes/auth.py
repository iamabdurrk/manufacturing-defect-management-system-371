"""Authentication routes: signup and login."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.schemas.auth import LoginSchema, SignupSchema
from app.utils.errors import abort_json

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/signup")
def signup():
    """Create user account and return JWT token + user."""
    data = request.get_json(silent=True) or {}
    schema = SignupSchema()
    errors = schema.validate(data)
    if errors:
        abort_json(422, "Validation error", errors=errors)

    service = request.app_ctx["services"]["auth"]
    resp = service.signup(schema.load(data))
    return jsonify(resp)


@bp.post("/login")
def login():
    """Login and return JWT token + user."""
    data = request.get_json(silent=True) or {}
    schema = LoginSchema()
    errors = schema.validate(data)
    if errors:
        abort_json(422, "Validation error", errors=errors)

    service = request.app_ctx["services"]["auth"]
    resp = service.login(schema.load(data))
    return jsonify(resp)
