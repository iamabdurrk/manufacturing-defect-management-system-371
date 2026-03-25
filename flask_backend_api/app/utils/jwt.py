"""JWT creation and verification."""

from __future__ import annotations

import datetime as dt
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import jwt
from flask import g, request

from app.utils.errors import abort_json

F = TypeVar("F", bound=Callable[..., Any])


# PUBLIC_INTERFACE
def create_access_token(
    *,
    secret: str,
    user_id: str,
    email: str,
    name: str,
    role: str,
    issuer: str,
    audience: str,
    exp_minutes: int,
) -> str:
    """Create an HS256 access token for a user."""
    now = dt.datetime.utcnow()
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "role": role,
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(*, secret: str, token: str, issuer: str, audience: str) -> dict[str, Any]:
    """Decode/validate JWT and return claims."""
    return cast(
        dict[str, Any],
        jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            issuer=issuer,
            audience=audience,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
        ),
    )


# PUBLIC_INTERFACE
def jwt_required(settings) -> Callable[[F], F]:
    """Decorator enforcing Authorization: Bearer <token> and populating g.user."""

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                abort_json(401, "Missing or invalid Authorization header")
            token = auth.split(" ", 1)[1].strip()
            try:
                claims = decode_token(
                    secret=settings.jwt_secret,
                    token=token,
                    issuer=settings.jwt_issuer,
                    audience=settings.jwt_audience,
                )
            except Exception:
                abort_json(401, "Invalid or expired token")

            g.user = {
                "id": claims.get("sub"),
                "email": claims.get("email"),
                "name": claims.get("name"),
                "role": claims.get("role"),
            }
            return fn(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
