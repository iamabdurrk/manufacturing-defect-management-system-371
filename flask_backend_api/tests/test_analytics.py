from __future__ import annotations

from unittest.mock import patch


def test_pareto_requires_auth(client):
    res = client.get("/api/analytics/pareto")
    assert res.status_code == 401


def test_pareto_success_forwards_query(client, auth_headers):
    with patch("app.routes.analytics.AnalyticsService") as AnalyticsService:
        AnalyticsService.return_value.pareto.return_value = {"items": [], "total": 0}
        res = client.get("/api/analytics/pareto?start=2025-01-01&end=2025-01-31", headers=auth_headers)

        # Verify the route forwards parsed args to service call
        AnalyticsService.return_value.pareto.assert_called_once_with(start="2025-01-01", end="2025-01-31")

    assert res.status_code == 200
    assert res.get_json()["total"] == 0


def test_trends_defaults_interval_to_day(client, auth_headers):
    with patch("app.routes.analytics.AnalyticsService") as AnalyticsService:
        AnalyticsService.return_value.trends.return_value = {"items": [], "interval": "day"}
        res = client.get("/api/analytics/trends", headers=auth_headers)

        AnalyticsService.return_value.trends.assert_called_once()
        _, kwargs = AnalyticsService.return_value.trends.call_args
        assert kwargs["interval"] == "day"

    assert res.status_code == 200
    assert res.get_json()["interval"] == "day"
