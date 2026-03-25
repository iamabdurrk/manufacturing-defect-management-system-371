from __future__ import annotations

from datetime import date
from typing import Any

from bson import ObjectId
from dateutil.parser import isoparse

from app.repositories.actions_repo import CorrectiveActionsRepository
from app.repositories.defects_repo import DefectsRepository
from app.repositories.users_repo import UsersRepository
from app.utils.errors import NotFoundError, ServiceError
from app.utils.serialization import serialize_doc


class ActionsService:
    """Corrective action service."""

    def __init__(self) -> None:
        self._actions = CorrectiveActionsRepository()
        self._defects = DefectsRepository()
        self._users = UsersRepository()

    def create_action(self, payload: dict[str, Any]) -> dict:
        defect = self._defects.find_by_id(ObjectId(payload["defect_id"]))
        if not defect:
            raise NotFoundError("Defect not found")

        owner = self._users.find_by_id(ObjectId(payload["owner_id"]))
        if not owner:
            raise NotFoundError("Owner not found")

        # Validate due_date parsable
        try:
            due = isoparse(payload["due_date"]).date()
        except Exception as e:
            raise ServiceError("Invalid due_date", code="invalid_due_date", http_status=400) from e

        status = payload.get("status") or "Open"
        doc = {
            "defect_id": ObjectId(payload["defect_id"]),
            "description": payload["description"],
            "owner_id": ObjectId(payload["owner_id"]),
            "due_date": due.isoformat(),
            "status": status,
            "completed_date": None,
        }
        created = self._actions.insert(doc)
        return serialize_doc(created)

    def update_action(self, action_id: str, payload: dict[str, Any]) -> dict:
        existing = self._actions.find_by_id(ObjectId(action_id))
        if not existing:
            raise NotFoundError("Action not found")

        update_fields: dict[str, Any] = {}
        if "description" in payload:
            update_fields["description"] = payload["description"]
        if "owner_id" in payload:
            owner = self._users.find_by_id(ObjectId(payload["owner_id"]))
            if not owner:
                raise NotFoundError("Owner not found")
            update_fields["owner_id"] = ObjectId(payload["owner_id"])
        if "due_date" in payload:
            try:
                due = isoparse(payload["due_date"]).date()
            except Exception as e:
                raise ServiceError("Invalid due_date", code="invalid_due_date", http_status=400) from e
            update_fields["due_date"] = due.isoformat()
        if "status" in payload:
            update_fields["status"] = payload["status"]
            if payload["status"] == "Complete":
                update_fields["completed_date"] = date.today().isoformat()
        if "completed_date" in payload:
            update_fields["completed_date"] = payload["completed_date"]

        updated = self._actions.update_fields(ObjectId(action_id), update_fields)
        if not updated:
            raise NotFoundError("Action not found")
        return serialize_doc(updated)

    def list_by_defect(self, defect_id: str) -> dict:
        defect = self._defects.find_by_id(ObjectId(defect_id))
        if not defect:
            raise NotFoundError("Defect not found")
        items = self._actions.list_by_defect(ObjectId(defect_id))
        return {"items": serialize_doc(items)}

    def list_overdue_dashboard(self) -> dict:
        today_iso = date.today().isoformat()
        overdue = self._actions.list_overdue(today_iso=today_iso)

        # Join minimal defect + owner info (application-side join)
        enriched = []
        for a in overdue:
            defect = self._defects.find_by_id(a["defect_id"])
            owner = self._users.find_by_id(a["owner_id"])
            due = isoparse(a["due_date"]).date()
            overdue_days = (date.today() - due).days
            enriched.append(
                {
                    "action": serialize_doc(a),
                    "defect": serialize_doc(defect) if defect else None,
                    "owner": serialize_doc({k: v for k, v in owner.items() if k != "password_hash"}) if owner else None,
                    "overdue_days": overdue_days,
                }
            )
        return {"items": enriched, "today": today_iso}
