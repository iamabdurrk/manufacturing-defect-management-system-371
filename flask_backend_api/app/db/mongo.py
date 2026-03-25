"""MongoDB connection and initialization utilities."""

from __future__ import annotations

from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.database import Database


@dataclass(frozen=True)
class Mongo:
    """Holds Mongo client and db handle."""

    client: MongoClient
    db: Database


def init_indexes(db: Database) -> None:
    """Create indexes used by queries (idempotent)."""
    db.users.create_index("email", unique=True)
    db.defects.create_index("created_at")
    db.defects.create_index([("status", 1), ("severity", 1)])
    db.defects.create_index("defect_type_id")
    db.defects.create_index("production_line")
    db.defects.create_index("part_number")

    db.rca.create_index("defect_id", unique=True)

    db.actions.create_index("defect_id")
    db.actions.create_index([("status", 1), ("due_date", 1)])
    db.actions.create_index("owner_id")

    db.uploads.create_index("created_at")


def create_mongo(mongodb_url: str, mongodb_db: str) -> Mongo:
    """Create Mongo connection and ensure indexes."""
    client = MongoClient(mongodb_url)
    db = client[mongodb_db]
    init_indexes(db)
    return Mongo(client=client, db=db)
