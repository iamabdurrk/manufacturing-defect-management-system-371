"""Defects, RCA, and export routes."""

from __future__ import annotations

from flask import Blueprint, Response, jsonify, request

from app.schemas.defects import DefectCreateSchema, DefectUpdateSchema, RootCauseUpsertSchema
from app.utils.errors import abort_json
from app.utils.jwt import jwt_required

bp = Blueprint("defects", __name__, url_prefix="/api/defects")


@bp.get("")
def list_defects():
    """List defects (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()  # populate g.user

    svc = request.app_ctx["services"]["defects"]
    return jsonify(svc.list_defects())


@bp.post("")
def create_defect():
    """Create a defect (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    data = request.get_json(silent=True) or {}
    schema = DefectCreateSchema()
    errors = schema.validate(data)
    if errors:
        abort_json(422, "Validation error", errors=errors)

    svc = request.app_ctx["services"]["defects"]
    created = svc.create_defect(schema.load(data), created_by=request.app_ctx["current_user"]())
    return jsonify(created)


@bp.get("/<defect_id>")
def get_defect(defect_id: str):
    """Get a single defect by id (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    svc = request.app_ctx["services"]["defects"]
    return jsonify(svc.get_defect(defect_id))


@bp.put("/<defect_id>")
def update_defect(defect_id: str):
    """Update defect fields (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    data = request.get_json(silent=True) or {}
    schema = DefectUpdateSchema()
    errors = schema.validate(data)
    if errors:
        abort_json(422, "Validation error", errors=errors)

    svc = request.app_ctx["services"]["defects"]
    updated = svc.update_defect(defect_id, schema.load(data))
    return jsonify(updated)


@bp.get("/<defect_id>/rca")
def get_rca(defect_id: str):
    """Get RCA for a defect (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    svc = request.app_ctx["services"]["defects"]
    return jsonify(svc.get_rca(defect_id))


@bp.post("/<defect_id>/rca")
def upsert_rca(defect_id: str):
    """Create or update RCA for a defect (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    data = request.get_json(silent=True) or {}
    schema = RootCauseUpsertSchema()
    errors = schema.validate(data)
    if errors:
        abort_json(422, "Validation error", errors=errors)

    svc = request.app_ctx["services"]["defects"]
    saved = svc.upsert_rca(defect_id, schema.load(data), updated_by=request.app_ctx["current_user"]())
    return jsonify(saved)


@bp.get("/<defect_id>/export")
def export_defect(defect_id: str):
    """Export defect report as PDF (JWT required)."""
    settings = request.app_ctx["settings"]
    jwt_required(settings)(lambda: None)()

    defects_svc = request.app_ctx["services"]["defects"]
    actions_svc = request.app_ctx["services"]["actions"]
    export_svc = request.app_ctx["services"]["export"]

    defect = defects_svc.get_defect(defect_id)
    rca = defects_svc.get_rca(defect_id)
    # actions list may be large; filter in-memory for this defect (simple approach)
    actions = [a for a in actions_svc.list_actions() if a.get("defect_id") == defect_id]

    pdf_bytes = export_svc.build_defect_pdf(defect=defect, rca=rca, actions=actions)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="defect_{defect_id}.pdf"'},
    )
