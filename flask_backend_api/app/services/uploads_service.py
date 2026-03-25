"""File upload and serving service."""

from __future__ import annotations

import os
import pathlib
from typing import Any

from app.utils.errors import abort_json
from app.utils.serialization import iso_now, oid


class UploadsService:
    """Handles file uploads and retrieval."""

    def __init__(self, *, uploads_repo, settings):
        self._uploads = uploads_repo
        self._settings = settings

    def ensure_upload_dir(self) -> str:
        upload_dir = self._settings.upload_dir
        pathlib.Path(upload_dir).mkdir(parents=True, exist_ok=True)
        return upload_dir

    def save_upload(self, *, storage_file) -> dict[str, Any]:
        if storage_file is None:
            abort_json(422, "No file provided", errors={"file": "required"})

        upload_dir = self.ensure_upload_dir()

        filename = storage_file.filename or "upload.bin"
        content_type = storage_file.mimetype or "application/octet-stream"

        # Create a Mongo metadata doc first to get an id for filename.
        meta = {
            "filename": filename,
            "content_type": content_type,
            "size": 0,
            "created_at": iso_now(),
        }
        file_id = self._uploads.insert(meta)

        # Save to disk as <id>_<originalname>
        safe_name = "".join(c for c in filename if c.isalnum() or c in ("-", "_", ".", " ")).strip() or "file"
        disk_name = f"{file_id}_{safe_name}"
        disk_path = os.path.join(upload_dir, disk_name)
        storage_file.save(disk_path)
        size = os.path.getsize(disk_path)

        # Update metadata
        self._uploads._col.update_one(  # intentional internal use
            {"_id": oid(file_id)},
            {"$set": {"size": size, "disk_name": disk_name, "disk_path": disk_path}},
        )

        return {
            "file_id": file_id,
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "url": f"/uploads/{file_id}",
        }

    def resolve_disk_path(self, file_id: str) -> dict[str, Any]:
        try:
            _id = oid(file_id)
        except ValueError:
            abort_json(422, "Invalid file_id")
        meta = self._uploads.find_by_id(_id)
        if not meta:
            abort_json(404, "File not found")
        if not meta.get("disk_path"):
            abort_json(404, "File not found")
        return meta
