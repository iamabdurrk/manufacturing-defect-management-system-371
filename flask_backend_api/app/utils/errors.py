from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ServiceError(Exception):
    """Base class for business/service errors."""

    message: str
    code: str = "service_error"
    details: Optional[dict[str, Any]] = None
    http_status: int = 400


class NotFoundError(ServiceError):
    """Raised when an entity is not found."""

    def __init__(self, message: str = "Not found", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="not_found", details=details, http_status=404)


class UnauthorizedError(ServiceError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="unauthorized", details=details, http_status=401)


class ForbiddenError(ServiceError):
    """Raised when user is not allowed to perform an action."""

    def __init__(self, message: str = "Forbidden", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="forbidden", details=details, http_status=403)


class ConflictError(ServiceError):
    """Raised when a unique/constraint conflict occurs."""

    def __init__(self, message: str = "Conflict", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="conflict", details=details, http_status=409)
