from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId


# PUBLIC_INTERFACE
def to_object_id(id_str: str) -> ObjectId:
    """Convert string to ObjectId with validation."""
    try:
        return ObjectId(id_str)
    except Exception as e:
        raise ValueError("Invalid id") from e


def _dt_to_iso(dt_val: datetime) -> str:
    if dt_val.tzinfo is None:
        dt_val = dt_val.replace(tzinfo=timezone.utc)
    return dt_val.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# PUBLIC_INTERFACE
def serialize_doc(doc: Any) -> Any:
    """
    Recursively serialize MongoDB documents for JSON responses.
    - ObjectId -> str
    - datetime -> ISO string
    """
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return _dt_to_iso(doc)
    if isinstance(doc, list):
        return [serialize_doc(x) for x in doc]
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    return doc
