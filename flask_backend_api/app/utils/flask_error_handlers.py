from __future__ import annotations

from flask import Flask, jsonify

from app.utils.errors import ServiceError


# PUBLIC_INTERFACE
def register_error_handlers(app: Flask) -> None:
    """Register consistent JSON error responses for the API."""

    @app.errorhandler(ServiceError)
    def _handle_service_error(err: ServiceError):
        payload = {"error": {"code": err.code, "message": err.message, "details": err.details or {}}}
        return jsonify(payload), err.http_status

    @app.errorhandler(Exception)
    def _handle_unexpected(err: Exception):
        payload = {"error": {"code": "internal_error", "message": "Internal server error"}}
        return jsonify(payload), 500
