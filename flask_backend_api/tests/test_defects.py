from __future__ import annotations

from unittest.mock import patch


def test_list_defects_requires_auth(client):
    res = client.get("/api/defects")
    assert res.status_code == 401


def test_list_defects_success(client, auth_headers):
    with patch("app.routes.defects.DefectsService") as DefectsService:
        DefectsService.return_value.list_defects.return_value = {"items": [], "total": 0, "page": 1, "limit": 50}
        res = client.get("/api/defects", headers=auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["items"] == []
    assert data["total"] == 0


def test_create_defect_success(client, auth_headers):
    payload = {
        "part_number": "PN-1",
        "defect_type_id": "507f1f77bcf86cd799439011",
        "quantity_affected": 2,
        "production_line": "LineA",
        "shift": "Day",
    }

    with patch("app.routes.defects.DefectsService") as DefectsService:
        DefectsService.return_value.create_defect.return_value = {
            "_id": "d1",
            "part_number": "PN-1",
            "defect_type_id": "507f1f77bcf86cd799439011",
            "quantity_affected": 2,
            "production_line": "LineA",
            "shift": "Day",
            "severity": "Minor",
            "status": "New",
            "timeline": [{"status": "New"}],
        }
        res = client.post("/api/defects", json=payload, headers=auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["_id"] == "d1"
    assert data["status"] == "New"


def test_update_defect_rca_gating_returns_400(client, auth_headers):
    """
    Business rule: cannot move to 'Under Investigation' unless RCA exists AND at least one why exists.

    We enforce this in tests by making DefectsService.update_defect raise ServiceError with rca_required.
    """
    with patch("app.routes.defects.DefectsService") as DefectsService:
        from app.utils.errors import ServiceError

        DefectsService.return_value.update_defect.side_effect = ServiceError(
            message="RCA required before moving to Under Investigation",
            code="rca_required",
            details={"required": ["root_cause", "at_least_one_why"]},
            http_status=400,
        )

        res = client.put(
            "/api/defects/507f1f77bcf86cd799439012",
            json={"status": "Under Investigation"},
            headers=auth_headers,
        )

    assert res.status_code == 400
    body = res.get_json()
    assert body["error"]["code"] == "rca_required"
    assert "RCA required" in body["error"]["message"]
    assert body["error"]["details"]["required"] == ["root_cause", "at_least_one_why"]


def test_get_defect_success(client, auth_headers):
    with patch("app.routes.defects.DefectsService") as DefectsService:
        DefectsService.return_value.get_defect.return_value = {"_id": "d1", "status": "New"}
        res = client.get("/api/defects/507f1f77bcf86cd799439012", headers=auth_headers)

    assert res.status_code == 200
    assert res.get_json()["_id"] == "d1"
