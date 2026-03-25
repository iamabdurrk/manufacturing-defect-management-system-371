from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId

from app.repositories.defects_repo import DefectsRepository, DefectTypesRepository
from app.repositories.rca_repo import RootCausesRepository
from app.repositories.severity_rules_repo import SeverityRulesRepository
from app.utils.errors import NotFoundError, ServiceError
from app.utils.serialization import serialize_doc


class DefectsService:
    """
    Defects service (business rules live here, not routes):
    - Create defects
    - Update defects with workflow enforcement
    - List defects
    - Apply severity rules (basic condition matching)
    """

    def __init__(self) -> None:
        self._defects = DefectsRepository()
        self._types = DefectTypesRepository()
        self._rca = RootCausesRepository()
        self._rules = SeverityRulesRepository()

    def _apply_severity_rules(self, defect: dict[str, Any]) -> Optional[str]:
        """
        Very small rule engine:
        - severity_rules documents contain a `condition` dict like:
            {"defect_type_id": "<id>"} or {"production_line": "A1"} etc.
        - If all keys match, set rule severity.
        """
        rules = self._rules.list()
        for r in rules:
            cond = r.get("condition") or {}
            ok = True
            for k, v in cond.items():
                if defect.get(k) != v:
                    ok = False
                    break
            if ok:
                return r.get("severity")
        return None

    def create_defect(self, payload: dict[str, Any], created_by: str) -> dict:
        defect_type = self._types.find_by_id(ObjectId(payload["defect_type_id"]))
        if not defect_type:
            raise NotFoundError("Defect type not found")

        status = payload.get("status") or "New"
        severity = payload.get("severity")
        # Rule-based severity if not provided
        if not severity:
            computed = self._apply_severity_rules(payload)
            if computed:
                severity = computed
            else:
                severity = "Minor"

        doc = {
            "part_number": payload["part_number"],
            "defect_type_id": ObjectId(payload["defect_type_id"]),
            "quantity_affected": payload["quantity_affected"],
            "production_line": payload["production_line"],
            "shift": payload["shift"],
            "severity": severity,
            "status": status,
            "photo_file_id": ObjectId(payload["photo_file_id"]) if payload.get("photo_file_id") else None,
            "created_by": created_by,
            "timeline": [{"status": status, "at": datetime.now(timezone.utc), "by": created_by}],
        }
        created = self._defects.insert(doc)
        return serialize_doc(created)

    def list_defects(self, query: dict[str, Any]) -> dict:
        limit = int(query.get("limit", 50))
        page = int(query.get("page", 1))
        limit = max(1, min(limit, 200))
        page = max(1, page)
        skip = (page - 1) * limit

        filters: dict[str, Any] = {}
        if query.get("status"):
            filters["status"] = query["status"]
        if query.get("severity"):
            filters["severity"] = query["severity"]
        if query.get("production_line"):
            filters["production_line"] = query["production_line"]

        total = self._defects.count(filters)
        items = self._defects.list(filters, limit=limit, skip=skip)
        return {"items": serialize_doc(items), "total": total, "page": page, "limit": limit}

    def get_defect(self, defect_id: str) -> dict:
        doc = self._defects.find_by_id(ObjectId(defect_id))
        if not doc:
            raise NotFoundError("Defect not found")
        return serialize_doc(doc)

    def update_defect(self, defect_id: str, payload: dict[str, Any], updated_by: str) -> dict:
        existing = self._defects.find_by_id(ObjectId(defect_id))
        if not existing:
            raise NotFoundError("Defect not found")

        new_status = payload.get("status")
        if new_status and new_status != existing.get("status"):
            # Workflow enforcement rule:
            # status cannot change -> "Under Investigation" without RCA existing AND at least one why entry.
            if new_status == "Under Investigation":
                rc = self._rca.get_root_cause(ObjectId(defect_id))
                whys = self._rca.list_five_whys(ObjectId(defect_id))
                if not rc or len(whys) < 1:
                    raise ServiceError(
                        message="RCA required before moving to Under Investigation",
                        code="rca_required",
                        details={"required": ["root_cause", "at_least_one_why"]},
                        http_status=400,
                    )

        update_fields: dict[str, Any] = {}
        for k in ["part_number", "quantity_affected", "production_line", "shift", "severity", "status"]:
            if k in payload:
                update_fields[k] = payload[k]

        if "defect_type_id" in payload:
            dt_doc = self._types.find_by_id(ObjectId(payload["defect_type_id"]))
            if not dt_doc:
                raise NotFoundError("Defect type not found")
            update_fields["defect_type_id"] = ObjectId(payload["defect_type_id"])

        if "photo_file_id" in payload:
            update_fields["photo_file_id"] = ObjectId(payload["photo_file_id"]) if payload["photo_file_id"] else None

        if new_status and new_status != existing.get("status"):
            timeline = existing.get("timeline", [])
            timeline.append({"status": new_status, "at": datetime.now(timezone.utc), "by": updated_by})
            update_fields["timeline"] = timeline

        updated = self._defects.update_fields(ObjectId(defect_id), update_fields)
        if not updated:
            raise NotFoundError("Defect not found")
        return serialize_doc(updated)
