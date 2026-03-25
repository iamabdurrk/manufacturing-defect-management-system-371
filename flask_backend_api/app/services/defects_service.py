"""Defects + RCA service with business rules."""

from __future__ import annotations



from app.utils.errors import abort_json
from app.utils.serialization import dump_oid, iso_now, oid


class DefectsService:
    """Business logic for defects, including RCA gating rules."""

    def __init__(self, *, defects_repo, rca_repo):
        self._defects = defects_repo
        self._rca = rca_repo

    def list_defects(self) -> list[dict]:
        return [dump_oid(d) for d in self._defects.list_all()]

    def create_defect(self, payload: dict, created_by: dict) -> dict:
        doc = {
            "part_number": payload["part_number"],
            "defect_type_id": payload["defect_type_id"],
            "quantity_affected": payload["quantity_affected"],
            "production_line": payload["production_line"],
            "shift": payload["shift"],
            "severity": payload.get("severity") or "Minor",
            "status": payload.get("status") or "Open",
            "photo_file_id": payload.get("photo_file_id"),
            "created_at": iso_now(),
            "updated_at": iso_now(),
            "created_by": created_by,
        }
        defect_id = self._defects.insert(doc)
        doc["id"] = defect_id
        return doc

    def get_defect(self, defect_id: str) -> dict:
        try:
            _id = oid(defect_id)
        except ValueError:
            abort_json(422, "Invalid defect_id")
        doc = self._defects.find_by_id(_id)
        if not doc:
            abort_json(404, "Defect not found")
        return dump_oid(doc)

    def update_defect(self, defect_id: str, payload: dict) -> dict:
        try:
            _id = oid(defect_id)
        except ValueError:
            abort_json(422, "Invalid defect_id")

        existing = self._defects.find_by_id(_id)
        if not existing:
            abort_json(404, "Defect not found")

        # RCA gating rule:
        # If severity is Critical and status is being set to a non-open state,
        # require RCA to exist.
        new_status = payload.get("status")
        new_severity = payload.get("severity", existing.get("severity"))
        if new_status and new_status != existing.get("status"):
            if (new_severity == "Critical") and (new_status in ["In Review", "Closed", "Complete"]):
                rca = self._rca.find_by_defect_id(_id)
                if not rca:
                    abort_json(422, "RCA required before moving Critical defect forward")

        updates = {**payload, "updated_at": iso_now()}
        updated = self._defects.update_by_id(_id, updates)
        return dump_oid(updated) if updated else self.get_defect(defect_id)

    def get_rca(self, defect_id: str) -> dict:
        try:
            _id = oid(defect_id)
        except ValueError:
            abort_json(422, "Invalid defect_id")

        # ensure defect exists
        if not self._defects.find_by_id(_id):
            abort_json(404, "Defect not found")

        rca = self._rca.find_by_defect_id(_id)
        if not rca:
            return {"defect_id": defect_id, "method": None}
        rca = dump_oid(rca)
        # defect_id in rca is ObjectId; expose as string
        if "defect_id" in rca:
            rca["defect_id"] = defect_id
        return rca

    def upsert_rca(self, defect_id: str, payload: dict, updated_by: dict) -> dict:
        try:
            _id = oid(defect_id)
        except ValueError:
            abort_json(422, "Invalid defect_id")

        if not self._defects.find_by_id(_id):
            abort_json(404, "Defect not found")

        doc = {
            "defect_id": _id,
            "method": payload["method"],
            "five_whys": payload.get("five_whys") or [],
            "fishbone": payload.get("fishbone") or {},
            "updated_at": iso_now(),
            "updated_by": updated_by,
        }
        saved = self._rca.upsert(doc)
        saved = dump_oid(saved)
        saved["defect_id"] = defect_id
        return saved
