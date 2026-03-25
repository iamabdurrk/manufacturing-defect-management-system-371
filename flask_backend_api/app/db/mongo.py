from __future__ import annotations

import os
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

_client: Optional[MongoClient] = None


def _build_mongo_uri_from_db_connection_txt() -> Optional[str]:
    """
    Attempt to read MongoDB URI from the database container's db_connection.txt.

    The database container writes a line like:
        mongosh mongodb://user:pass@host:port/db?authSource=admin
    """
    candidates = [
        # Common relative path between containers in monorepo workspace.
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "..",
                "manufacturing-defect-management-system-372",
                "database",
                "db_connection.txt",
            )
        )
    ]
    for path in candidates:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    line = f.readline().strip()
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1]
        except Exception:
            # Non-fatal; we will fall back to env vars.
            continue
    return None


# PUBLIC_INTERFACE
def get_mongo_client(mongo_url: Optional[str] = None) -> MongoClient:
    """Get a process-wide MongoClient instance."""
    global _client
    if _client is not None:
        return _client

    uri = mongo_url or os.getenv("MONGODB_URL") or _build_mongo_uri_from_db_connection_txt()
    if not uri:
        raise RuntimeError(
            "MongoDB connection is not configured. Set MONGODB_URL env var "
            "(or ensure database/db_connection.txt exists)."
        )

    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


# PUBLIC_INTERFACE
def get_db(db_name: Optional[str] = None) -> Database:
    """Get configured MongoDB database."""
    name = db_name or os.getenv("MONGODB_DB")
    if not name:
        # If URI already contains db, MongoClient.get_default_database() can work,
        # but we keep it explicit and predictable.
        raise RuntimeError("MongoDB database name is not configured. Set MONGODB_DB env var.")
    return get_mongo_client()[name]
