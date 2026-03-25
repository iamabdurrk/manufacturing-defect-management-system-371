"""Health check routes."""

from __future__ import annotations

from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/")
def health():
    """Health check endpoint used by frontend and monitoring."""
    return jsonify({"status": "ok"})
