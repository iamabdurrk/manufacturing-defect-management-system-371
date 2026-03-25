"""Flask application factory.

Registers routes, connects to MongoDB, wires repositories/services, and configures CORS + error handling.
"""

from __future__ import annotations

from flask import Flask, g, request
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import Settings
from app.db.mongo import create_mongo
from app.repositories.actions_repo import ActionsRepository
from app.repositories.defects_repo import DefectsRepository
from app.repositories.rca_repo import RcaRepository
from app.repositories.uploads_repo import UploadsRepository
from app.repositories.users_repo import UsersRepository
from app.routes.actions import bp as actions_bp
from app.routes.analytics import bp as analytics_bp
from app.routes.auth import bp as auth_bp
from app.routes.dashboard import bp as dashboard_bp
from app.routes.defects import bp as defects_bp
from app.routes.health import bp as health_bp
from app.routes.uploads import bp_api as uploads_api_bp, bp_public as uploads_public_bp
from app.services.actions_service import ActionsService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.defects_service import DefectsService
from app.services.export_service import ExportService
from app.services.uploads_service import UploadsService
from app.utils.errors import ApiError


def create_app() -> Flask:
    """Create and configure the Flask app instance."""
    load_dotenv()

    app = Flask(__name__)
    settings = Settings.from_env()

    # Upload size limit
    app.config["MAX_CONTENT_LENGTH"] = settings.max_content_length

    # CORS (allow Authorization header for JWT)
    if settings.cors_origins:
        CORS(app, origins=settings.cors_origins, supports_credentials=False)
    else:
        CORS(app)  # permissive fallback for dev

    mongo = create_mongo(settings.mongodb_url, settings.mongodb_db)
    db = mongo.db

    # wire repos/services
    repos = {
        "users": UsersRepository(db),
        "defects": DefectsRepository(db),
        "rca": RcaRepository(db),
        "actions": ActionsRepository(db),
        "uploads": UploadsRepository(db),
    }
    services = {
        "auth": AuthService(users_repo=repos["users"], settings=settings),
        "defects": DefectsService(defects_repo=repos["defects"], rca_repo=repos["rca"]),
        "actions": ActionsService(actions_repo=repos["actions"], defects_repo=repos["defects"], rca_repo=repos["rca"]),
        "analytics": AnalyticsService(db=db),
        "uploads": UploadsService(uploads_repo=repos["uploads"], settings=settings),
        "export": ExportService(),
    }

    # Attach app context data into request for easy access in blueprints.
    @app.before_request
    def _attach_ctx():
        request.app_ctx = {
            "settings": settings,
            "db": db,
            "repos": repos,
            "services": services,
            "current_user": lambda: getattr(g, "user", None),
        }

    # Global error handlers
    @app.errorhandler(ApiError)
    def _handle_api_error(err: ApiError):
        return err.to_response()

    @app.errorhandler(404)
    def _handle_404(_):
        return {"message": "Not found"}, 404

    @app.errorhandler(413)
    def _handle_too_large(_):
        return {"message": "File too large"}, 413

    @app.errorhandler(Exception)
    def _handle_unexpected(err: Exception):
        # Avoid leaking internals; keep message generic.
        app.logger.exception("Unhandled exception: %s", err)
        return {"message": "Internal server error"}, 500

    # Ensure created_at_dt exists for analytics matching.
    # We keep this lightweight: if documents are missing the dt field, add on startup.
    try:
        db.defects.update_many(
            {"created_at_dt": {"$exists": False}, "created_at": {"$exists": True}},
            [{"$set": {"created_at_dt": {"$dateFromString": {"dateString": "$created_at"}}}}],
        )
    except Exception:
        # Not fatal (some mongo versions disallow pipeline updates); analytics will still work without date range filter.
        pass

    # Register routes
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(defects_bp)
    app.register_blueprint(actions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(uploads_api_bp)
    app.register_blueprint(uploads_public_bp)

    return app
