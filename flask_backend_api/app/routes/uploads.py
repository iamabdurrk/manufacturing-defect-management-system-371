"""Upload routes."""

from __future__ import annotations

import os

from flask import Blueprint, jsonify, request, send_file

from app.utils.errors import abort_json
from app.utils.jwt import jwt_required

bp_api = Blueprint("uploads_api", __name__, url_prefix="/api/uploads")
bp_public = Blueprint("uploads_public", __name__, url_prefix="/uploads")


@bp_api.post("")
def upload():
    """Upload a file via multipart/form-data with field name 'file' (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    svc = request.app_ctx["services"]["uploads"]
    storage_file = request.files.get("file")
    saved = svc.save_upload(storage_file=storage_file)
    return jsonify(saved)


@bp_api.get("/<file_id>")
def get_upload_meta(file_id: str):
    """Get upload metadata (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    svc = request.app_ctx["services"]["uploads"]
    meta = svc.resolve_disk_path(file_id)
    meta["id"] = str(meta["_id"])
    del meta["_id"]
    return jsonify(meta)


@bp_public.get("/<file_id>")
def serve_public(file_id: str):
    """Serve uploaded content publicly (JWT optional)."""
    svc = request.app_ctx["services"]["uploads"]
    meta = svc.resolve_disk_path(file_id)
    path = meta["disk_path"]
    if not os.path.exists(path):
        abort_json(404, "File not found")
    return send_file(path, mimetype=meta.get("content_type") or "application/octet-stream", as_attachment=False)
