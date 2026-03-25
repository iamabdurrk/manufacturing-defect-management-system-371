from __future__ import annotations


def test_health_ok(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.is_json
    assert res.get_json() == {"message": "Healthy"}


def test_protected_endpoint_requires_bearer_token(client):
    # Any endpoint using get_current_user_claims() should return 401 when missing Bearer token.
    res = client.get("/api/defects")
    assert res.status_code == 401
    body = res.get_json()
    assert body["error"]["code"] == "unauthorized"
    assert "Bearer" in body["error"]["message"]
