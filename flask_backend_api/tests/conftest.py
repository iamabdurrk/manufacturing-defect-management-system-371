from __future__ import annotations

import pytest

from app import app as flask_app


@pytest.fixture(scope="session")
def app():
    """
    Session-scoped Flask app fixture.

    We set a deterministic JWT secret for tests so we can mint tokens without relying
    on CI-provided secrets.
    """
    flask_app.config.update(
        TESTING=True,
        JWT_SECRET="test-jwt-secret",
    )
    return flask_app


@pytest.fixture()
def client(app):
    """Flask test client fixture."""
    return app.test_client()


@pytest.fixture()
def auth_headers(app) -> dict[str, str]:
    """
    Build Authorization header with a valid Bearer token.

    Uses app.config['JWT_SECRET'] set by the `app` fixture.
    """
    with app.app_context():
        from app.utils.jwt_utils import create_access_token

        token = create_access_token(user_id="user_1", email="user@example.com", role="admin")
    return {"Authorization": f"Bearer {token}"}
