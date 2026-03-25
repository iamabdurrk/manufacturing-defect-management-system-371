from __future__ import annotations

import os
import secrets
from typing import Any

from bson import ObjectId
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.repositories.uploads_repo import UploadsRepository
from app.utils.errors import NotFoundError, ServiceError
from app.utils.serialization import serialize_doc


class UploadsService:
    """File upload service storing files locally and tracking metadata in MongoDB."""

    def __init__(self) -> None:
        self._uploads = UploadsRepository()

    def save_upload(self, file: FileStorage) -> dict[str, Any]:
        if not file or not file.filename:
            raise ServiceError("No file provided", code="no_file", http_status=400)

        upload_dir = current_app.config["UPLOAD_DIR"]
        os.makedirs(upload_dir, exist_ok=True)

        safe = secure_filename(file.filename)
        token = secrets.token_hex(12)
        stored_name = f"{token}__{safe}"
        full_path = os.path.join(upload_dir, stored_name)

        file.save(full_path)
        size = os.path.getsize(full_path)
        content_type = file.mimetype or "application/octet-stream"

        meta = self._uploads.insert(filename=safe, content_type=content_type, size=size, path=full_path)
        base = current_app.config.get("BACKEND_URL", "").rstrip("/")
        url = f"{base}{current_app.config.get('PUBLIC_UPLOADS_ROUTE', '/uploads')}/{str(meta['_id'])}"
        return serialize_doc({"file_id": meta["_id"], "filename": safe, "content_type": content_type, "size": size, "url": url})

    def get_file_meta(self, file_id: str) -> dict:
        doc = self._uploads.find_by_id(ObjectId(file_id))
        if not doc:
            raise NotFoundError("File not found")
        return doc
