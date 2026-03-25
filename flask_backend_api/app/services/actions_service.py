"""Corrective actions service with RCA gating and overdue logic."""

from __future__ import annotations

import datetime as dt

from app.utils.errors import abort_json
from app.utils.serialization import dump_oid, iso_now, oid, parse_date


class ActionsService:
    """Business logic for corrective actions."""

    def __init__(self, *, actions_repo, defects_repo, rca_repo):
        self._actions = actions_repo
        self._defects = defects_repo
        self._rca = rca_repo

    def list_actions(self) -> list[dict]:
        return [dump_oid(a) for a in self._actions.list_all()]

    def create_action(self, payload: dict, created_by: dict) -> dict:
        try:
            defect_oid = oid(payload["defect_id"])
        except ValueError:
            abort_json(422, "Invalid defect_id")

        defect = self._defects.find_by_id(defect_oid)
        if not defect:
            abort_json(404, "Defect not found")

        if defect.get("severity") == "Critical":
            rca = self._rca.find_by_defect_id(defect_oid)
            if not rca:
                abort_json(422, "RCA required before creating actions for Critical defects")

        due_dt = parse_date(payload["due_date"])
        doc = {
            "defect_id": defect_oid,
            "description": payload["description"],
            "owner_id": payload["owner_id"],
            "due_date": payload["due_date"],
            "due_date_dt": due_dt,
            "status": payload.get("status") or "Open",
            "completed_date": None,
            "created_at": iso_now(),
            "updated_at": iso_now(),
            "created_by": created_by,
        }
        action_id = self._actions.insert(doc)
        doc["id"] = action_id
        doc["defect_id"] = payload["defect_id"]
        return doc

    def update_action(self, action_id: str, payload: dict) -> dict:
        try:
            _id = oid(action_id)
        except ValueError:
            abort_json(422, "Invalid action_id")

        existing = self._actions.find_by_id(_id)
        if not existing:
            abort_json(404, "Action not found")

        updates = dict(payload)
        if "due_date" in updates:
            updates["due_date_dt"] = parse_date(updates["due_date"])
        if updates.get("status") == "Complete" and not updates.get("completed_date"):
            updates["completed_date"] = iso_now()
        updates["updated_at"] = iso_now()

        updated = self._actions.update_by_id(_id, updates)
        if not updated:
            abort_json(404, "Action not found")

        updated = dump_oid(updated)
        updated["defect_id"] = str(updated.get("defect_id")) if updated.get("defect_id") else None
        return updated

    def list_overdue(self) -> list[dict]:
        now_dt = dt.datetime.utcnow()
        results = self._actions.list_overdue(now_dt)
        out = []
        for a in results:
            a = dump_oid(a)
            a["defect_id"] = str(a.get("defect_id")) if a.get("defect_id") else None
            out.append(a)
        return out
