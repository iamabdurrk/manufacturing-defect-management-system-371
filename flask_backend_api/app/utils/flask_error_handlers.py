from __future__ import annotations

from flask import Flask, jsonify

from app.utils.errors import ServiceError


# PUBLIC_INTERFACE
def register_error_handlers(app: Flask) -> None:
    """Register consistent JSON error responses for the API.

    Notes:
        We intentionally convert certain configuration/runtime errors into a
        predictable JSON error response so the frontend can display an actionable
        message (e.g., missing JWT secret).
    """

    @app.errorhandler(ServiceError)
    def _handle_service_error(err: ServiceError):
        payload = {"error": {"code": err.code, "message": err.message, "details": err.details or {}}}
        return jsonify(payload), err.http_status

    @app.errorhandler(RuntimeError)
    def _handle_runtime_error(err: RuntimeError):
        """
        Handle misconfiguration errors (e.g., missing JWT_SECRET).

        We return 503 to indicate the server is not ready due to configuration.
        """
        msg = str(err) or "Runtime error"
        if "JWT_SECRET" in msg:
            payload = {
                "error": {
                    "code": "server_misconfigured",
                    "message": "Authentication is not configured on the server (missing JWT secret).",
                    "details": {"missing": ["JWT_SECRET"]},
                }
            }
            return jsonify(payload), 503

        # Default RuntimeError handling: keep generic but not a 500 stacktrace leak.
        payload = {"error": {"code": "runtime_error", "message": "Server runtime error"}}
        return jsonify(payload), 500

    @app.errorhandler(Exception)
    def _handle_unexpected(err: Exception):
        payload = {"error": {"code": "internal_error", "message": "Internal server error"}}
        return jsonify(payload), 500
