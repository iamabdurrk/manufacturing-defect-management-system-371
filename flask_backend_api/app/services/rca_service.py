from __future__ import annotations

from bson import ObjectId

from app.repositories.rca_repo import RootCausesRepository
from app.repositories.defects_repo import DefectsRepository
from app.utils.errors import NotFoundError, ServiceError
from app.utils.serialization import serialize_doc


class RCAService:
    """Root Cause Analysis service (5WHY and Fishbone metadata)."""

    def __init__(self) -> None:
        self._rca = RootCausesRepository()
        self._defects = DefectsRepository()

    def upsert_rca(self, defect_id: str, payload: dict, user_id: str) -> dict:
        defect = self._defects.find_by_id(ObjectId(defect_id))
        if not defect:
            raise NotFoundError("Defect not found")

        method = payload["method"]
        rc = self._rca.upsert_root_cause(ObjectId(defect_id), method=method, created_by=user_id)

        if method == "5WHY":
            whys = payload.get("five_whys") or []
            whys = [w.strip() for w in whys if str(w).strip()]
            if len(whys) < 1:
                raise ServiceError("At least one 5-Why entry is required", code="why_required", http_status=400)
            self._rca.replace_five_whys(ObjectId(defect_id), rc["_id"], whys)

        # Fishbone support: accepted by API schema; not yet persisted beyond the root_cause method flag.
        # This avoids embedding business logic into routes while keeping the endpoint contract stable.
        if method == "FISHBONE":
            pass

        return {"root_cause": serialize_doc(rc), "five_whys": serialize_doc(self._rca.list_five_whys(ObjectId(defect_id)))}

    def get_rca(self, defect_id: str) -> dict:
        rc = self._rca.get_root_cause(ObjectId(defect_id))
        whys = self._rca.list_five_whys(ObjectId(defect_id))
        return {"root_cause": serialize_doc(rc) if rc else None, "five_whys": serialize_doc(whys)}
