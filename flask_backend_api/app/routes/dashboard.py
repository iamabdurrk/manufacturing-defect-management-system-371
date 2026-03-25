from flask_smorest import Blueprint
from flask.views import MethodView

from app.services.actions_service import ActionsService
from app.utils.jwt_utils import get_current_user_claims

blp = Blueprint("Dashboard", "dashboard", url_prefix="/api/dashboard", description="Dashboard endpoints")


@blp.route("/overdue-actions")
class OverdueActions(MethodView):
    """List overdue corrective actions."""

    def get(self):
        get_current_user_claims()
        return ActionsService().list_overdue_dashboard()
