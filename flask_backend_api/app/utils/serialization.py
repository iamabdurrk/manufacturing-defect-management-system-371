"""Serialization helpers for MongoDB documents."""

from __future__ import annotations

import datetime as dt

from bson import ObjectId
from dateutil import parser as dt_parser


def oid(value: str) -> ObjectId:
    """Convert string to ObjectId (raises ValueError on failure)."""
    try:
        return ObjectId(value)
    except Exception as e:
        raise ValueError("Invalid id") from e


def iso_now() -> str:
    """Current UTC time as ISO8601 string."""
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()


def parse_date(value: str) -> dt.datetime:
    """Parse an ISO date/datetime string."""
    return dt_parser.isoparse(value)


def dump_oid(doc: dict) -> dict:
    """Convert Mongo _id ObjectId to string id field."""
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc
