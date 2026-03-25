"""Application configuration sourced from environment variables.

Keeps sensitive values (Mongo URI, JWT secret) out of code and supports deployment configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _get_env(name: str, default: str | None = None) -> str | None:
    """Internal helper to read environment variables."""
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    """Immutable settings for the Flask API."""

    mongodb_url: str
    mongodb_db: str

    jwt_secret: str
    jwt_issuer: str
    jwt_audience: str
    jwt_exp_minutes: int

    upload_dir: str
    max_content_length: int

    cors_origins: list[str]

    @staticmethod
    def from_env() -> "Settings":
        """Create Settings from environment variables."""
        mongodb_url = _get_env("MONGODB_URL")
        mongodb_db = _get_env("MONGODB_DB")
        jwt_secret = _get_env("JWT_SECRET")

        if not mongodb_url or not mongodb_db or not jwt_secret:
            missing = [
                name
                for name, value in [
                    ("MONGODB_URL", mongodb_url),
                    ("MONGODB_DB", mongodb_db),
                    ("JWT_SECRET", jwt_secret),
                ]
                if not value
            ]
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        jwt_issuer = _get_env("JWT_ISSUER", "mdms") or "mdms"
        jwt_audience = _get_env("JWT_AUDIENCE", "mdms-web") or "mdms-web"
        jwt_exp_minutes = int(_get_env("JWT_EXP_MINUTES", "480") or "480")

        upload_dir = _get_env("UPLOAD_DIR", "./uploads") or "./uploads"
        max_content_length = int(_get_env("MAX_CONTENT_LENGTH", "15728640") or "15728640")

        # NOTE: Orchestration environments sometimes provide ALLOWED_ORIGINS instead of CORS_ORIGINS.
        # Support both to avoid preview/runtime CORS breakage.
        cors_raw = _get_env("CORS_ORIGINS", "") or _get_env("ALLOWED_ORIGINS", "") or ""
        cors_origins = [o.strip() for o in cors_raw.split(",") if o.strip()]

        return Settings(
            mongodb_url=mongodb_url,
            mongodb_db=mongodb_db,
            jwt_secret=jwt_secret,
            jwt_issuer=jwt_issuer,
            jwt_audience=jwt_audience,
            jwt_exp_minutes=jwt_exp_minutes,
            upload_dir=upload_dir,
            max_content_length=max_content_length,
            cors_origins=cors_origins,
        )
