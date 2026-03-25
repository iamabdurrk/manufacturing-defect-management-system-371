from __future__ import annotations

import datetime as dt
from typing import Any, Optional

import jwt
from flask import current_app, request

from .errors import UnauthorizedError


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


# PUBLIC_INTERFACE
def create_access_token(user_id: str, email: str, role: str) -> str:
    """Create a signed JWT access token for a user."""
    secret = current_app.config.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not configured.")

    exp_minutes = int(current_app.config.get("JWT_EXP_MINUTES", 480))
    now = _utcnow()
    payload: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iss": current_app.config.get("JWT_ISSUER", "mdms"),
        "aud": current_app.config.get("JWT_AUDIENCE", "mdms-web"),
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


# PUBLIC_INTERFACE
def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""
    secret = current_app.config.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not configured.")

    try:
        return jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience=current_app.config.get("JWT_AUDIENCE", "mdms-web"),
            issuer=current_app.config.get("JWT_ISSUER", "mdms"),
        )
    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedError("Token expired") from e
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError("Invalid token") from e


# PUBLIC_INTERFACE
def get_bearer_token() -> str:
    """Extract Bearer token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise UnauthorizedError("Missing Bearer token")
    return auth.split(" ", 1)[1].strip()


# PUBLIC_INTERFACE
def get_current_user_claims() -> dict[str, Any]:
    """Get current user's JWT claims (requires Authorization header)."""
    token = get_bearer_token()
    return decode_token(token)


# PUBLIC_INTERFACE
def require_roles(claims: dict[str, Any], allowed: Optional[set[str]] = None) -> None:
    """Validate that claims include an allowed role."""
    if allowed is None:
        return
    role = claims.get("role")
    if role not in allowed:
        raise UnauthorizedError("Insufficient role")
