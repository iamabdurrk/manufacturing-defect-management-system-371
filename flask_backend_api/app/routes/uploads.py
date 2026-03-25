from flask import send_file
from flask_smorest import Blueprint
from flask.views import MethodView

from app.schemas.uploads import UploadResponseSchema
from app.services.uploads_service import UploadsService
from app.utils.jwt_utils import get_current_user_claims

blp = Blueprint("Uploads", "uploads", url_prefix="/api/uploads", description="File upload endpoints")


@blp.route("")
class Upload(MethodView):
    """Upload a file (photo evidence)."""

    @blp.response(200, UploadResponseSchema)
    def post(self):
        get_current_user_claims()
        file = (  # type: ignore[assignment]
            (getattr(__import__("flask"), "request")).files.get("file")  # avoid circular import lint issues
        )
        return UploadsService().save_upload(file)


@blp.route("/<file_id>")
class UploadItem(MethodView):
    """Download a previously uploaded file by id."""

    def get(self, file_id: str):
        get_current_user_claims()
        meta = UploadsService().get_file_meta(file_id)
        return send_file(meta["path"], mimetype=meta.get("content_type") or "application/octet-stream", as_attachment=False)
