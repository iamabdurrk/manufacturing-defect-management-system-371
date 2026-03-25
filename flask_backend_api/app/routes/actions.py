from flask import request
from flask_smorest import Blueprint
from flask.views import MethodView

from app.schemas.defects import CorrectiveActionCreateSchema, CorrectiveActionUpdateSchema
from app.services.actions_service import ActionsService
from app.utils.jwt_utils import get_current_user_claims

blp = Blueprint("Actions", "actions", url_prefix="/api/actions", description="Corrective actions routes")


@blp.route("")
class ActionsCollection(MethodView):
    """Create corrective action."""

    @blp.arguments(CorrectiveActionCreateSchema)
    def post(self, payload):
        get_current_user_claims()
        return ActionsService().create_action(payload)

    def get(self):
        # Optional convenience: list by defect_id query param
        get_current_user_claims()
        defect_id = request.args.get("defect_id")
        if defect_id:
            return ActionsService().list_by_defect(defect_id)
        return {"items": []}


@blp.route("/<action_id>")
class ActionItem(MethodView):
    """Update corrective action."""

    @blp.arguments(CorrectiveActionUpdateSchema)
    def put(self, payload, action_id: str):
        get_current_user_claims()
        return ActionsService().update_action(action_id, payload)
