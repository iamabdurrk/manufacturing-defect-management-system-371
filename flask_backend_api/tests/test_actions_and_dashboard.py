from __future__ import annotations

from unittest.mock import patch


def test_create_action_success(client, auth_headers):
    payload = {
        "defect_id": "507f1f77bcf86cd799439012",
        "description": "Fix the jig",
        "owner_id": "507f1f77bcf86cd799439013",
        "due_date": "2025-01-15",
        "status": "Open",
    }

    with patch("app.routes.actions.ActionsService") as ActionsService:
        ActionsService.return_value.create_action.return_value = {"_id": "a1", **payload, "completed_date": None}
        res = client.post("/api/actions", json=payload, headers=auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["_id"] == "a1"
    assert data["status"] == "Open"


def test_update_action_success(client, auth_headers):
    payload = {"status": "Complete"}
    with patch("app.routes.actions.ActionsService") as ActionsService:
        ActionsService.return_value.update_action.return_value = {
            "_id": "a1",
            "status": "Complete",
            "completed_date": "2025-01-10",
        }
        res = client.put("/api/actions/507f1f77bcf86cd799439014", json=payload, headers=auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "Complete"
    assert data["completed_date"] is not None


def test_list_actions_by_defect_query_param(client, auth_headers):
    with patch("app.routes.actions.ActionsService") as ActionsService:
        ActionsService.return_value.list_by_defect.return_value = {"items": [{"_id": "a1"}]}
        res = client.get("/api/actions?defect_id=507f1f77bcf86cd799439012", headers=auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert data["items"][0]["_id"] == "a1"


def test_dashboard_overdue_actions_success(client, auth_headers):
    with patch("app.routes.dashboard.ActionsService") as ActionsService:
        ActionsService.return_value.list_overdue_dashboard.return_value = {"items": [], "today": "2025-01-10"}
        res = client.get("/api/dashboard/overdue-actions", headers=auth_headers)

    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data
    assert "today" in data
