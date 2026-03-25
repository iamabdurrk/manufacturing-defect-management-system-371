from flask import send_file
from flask_smorest import Blueprint
from flask.views import MethodView

from app.services.uploads_service import UploadsService

blp = Blueprint("PublicUploads", "public_uploads", url_prefix="/uploads", description="Public uploads serving (JWT optional)")


@blp.route("/<file_id>")
class PublicUploadItem(MethodView):
    """Serve uploads by id (used by frontend to render images)."""

    def get(self, file_id: str):
        meta = UploadsService().get_file_meta(file_id)
        return send_file(meta["path"], mimetype=meta.get("content_type") or "application/octet-stream", as_attachment=False)
