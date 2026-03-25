from __future__ import annotations

from unittest.mock import patch


def test_get_rca_success(client, auth_headers):
    with patch("app.routes.defects.RCAService") as RCAService:
        RCAService.return_value.get_rca.return_value = {"root_cause": None, "five_whys": []}
        res = client.get("/api/defects/507f1f77bcf86cd799439012/rca", headers=auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["root_cause"] is None
    assert data["five_whys"] == []


def test_upsert_rca_5why_requires_at_least_one_entry(client, auth_headers):
    # Schema allows empty list, but service rejects (why_required -> 400)
    payload = {"method": "5WHY", "five_whys": []}

    with patch("app.routes.defects.RCAService") as RCAService:
        from app.utils.errors import ServiceError

        RCAService.return_value.upsert_rca.side_effect = ServiceError(
            "At least one 5-Why entry is required", code="why_required", http_status=400
        )
        res = client.post(
            "/api/defects/507f1f77bcf86cd799439012/rca",
            json=payload,
            headers=auth_headers,
        )

    assert res.status_code == 400
    body = res.get_json()
    assert body["error"]["code"] == "why_required"


def test_upsert_rca_success(client, auth_headers):
    payload = {"method": "5WHY", "five_whys": ["Why 1"]}
    with patch("app.routes.defects.RCAService") as RCAService:
        RCAService.return_value.upsert_rca.return_value = {
            "root_cause": {"_id": "rc1", "method": "5WHY"},
            "five_whys": [{"why_level": 1, "description": "Why 1"}],
        }
        res = client.post(
            "/api/defects/507f1f77bcf86cd799439012/rca",
            json=payload,
            headers=auth_headers,
        )

    assert res.status_code == 200
    data = res.get_json()
    assert data["root_cause"]["method"] == "5WHY"
    assert data["five_whys"][0]["why_level"] == 1
