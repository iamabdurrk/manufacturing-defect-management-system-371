"""Error response utilities.

All API errors are returned as JSON with:
- message: string safe for UI
- errors: optional field-level details
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import jsonify


@dataclass(frozen=True)
class ApiError(Exception):
    """Structured API error that can be converted to a JSON response."""

    status_code: int
    message: str
    errors: dict[str, Any] | None = None

    def to_response(self):
        """Convert this exception to a Flask response."""
        payload: dict[str, Any] = {"message": self.message}
        if self.errors is not None:
            payload["errors"] = self.errors
        return jsonify(payload), self.status_code


def abort_json(status_code: int, message: str, errors: dict[str, Any] | None = None):
    """Raise an ApiError (to be handled globally)."""
    raise ApiError(status_code=status_code, message=message, errors=errors)
