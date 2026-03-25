from flask_smorest import Blueprint
from flask.views import MethodView

from app.schemas.analytics import ParetoQuerySchema, TrendsQuerySchema
from app.services.analytics_service import AnalyticsService
from app.utils.jwt_utils import get_current_user_claims

blp = Blueprint("Analytics", "analytics", url_prefix="/api/analytics", description="Analytics endpoints")


@blp.route("/pareto")
class Pareto(MethodView):
    """Pareto analytics endpoint."""

    @blp.arguments(ParetoQuerySchema, location="query")
    def get(self, args):
        get_current_user_claims()
        return AnalyticsService().pareto(start=args.get("start"), end=args.get("end"))


@blp.route("/trends")
class Trends(MethodView):
    """Trends analytics endpoint."""

    @blp.arguments(TrendsQuerySchema, location="query")
    def get(self, args):
        get_current_user_claims()
        interval = args.get("interval") or "day"
        return AnalyticsService().trends(
            start=args.get("start"),
            end=args.get("end"),
            interval=interval,
            production_line=args.get("production_line"),
            part_number=args.get("part_number"),
            defect_type_id=args.get("defect_type_id"),
        )
