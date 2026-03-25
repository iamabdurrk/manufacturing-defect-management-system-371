import io

from flask import request, send_file
from flask_smorest import Blueprint
from flask.views import MethodView

from app.schemas.defects import DefectCreateSchema, DefectUpdateSchema, RootCauseUpsertSchema
from app.services.defects_service import DefectsService
from app.services.pdf_service import PdfExportService
from app.services.rca_service import RCAService
from app.utils.jwt_utils import get_current_user_claims

blp = Blueprint("Defects", "defects", url_prefix="/api/defects", description="Defects and RCA routes")


@blp.route("")
class DefectsCollection(MethodView):
    """Create and list defects."""

    @blp.arguments(DefectCreateSchema)
    def post(self, payload):
        claims = get_current_user_claims()
        svc = DefectsService()
        return svc.create_defect(payload, created_by=claims["sub"])

    def get(self):
        get_current_user_claims()
        svc = DefectsService()
        return svc.list_defects(request.args.to_dict())


@blp.route("/<defect_id>")
class DefectItem(MethodView):
    """Get or update a defect."""

    def get(self, defect_id: str):
        get_current_user_claims()
        svc = DefectsService()
        return svc.get_defect(defect_id)

    @blp.arguments(DefectUpdateSchema)
    def put(self, payload, defect_id: str):
        claims = get_current_user_claims()
        svc = DefectsService()
        return svc.update_defect(defect_id, payload, updated_by=claims["sub"])


@blp.route("/<defect_id>/rca")
class DefectRCA(MethodView):
    """Upsert and fetch RCA for a defect."""

    def get(self, defect_id: str):
        get_current_user_claims()
        svc = RCAService()
        return svc.get_rca(defect_id)

    @blp.arguments(RootCauseUpsertSchema)
    def post(self, payload, defect_id: str):
        claims = get_current_user_claims()
        svc = RCAService()
        return svc.upsert_rca(defect_id, payload, user_id=claims["sub"])


@blp.route("/<defect_id>/export")
class DefectExport(MethodView):
    """Export an audit-ready PDF for a defect."""

    def get(self, defect_id: str):
        get_current_user_claims()
        pdf = PdfExportService().export_defect_pdf(defect_id)
        return send_file(
            io.BytesIO(pdf),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"defect_{defect_id}.pdf",
        )
