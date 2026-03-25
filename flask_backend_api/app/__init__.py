from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .config import Config
from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.defects import blp as defects_blp
from .routes.actions import blp as actions_blp
from .routes.dashboard import blp as dashboard_blp
from .routes.analytics import blp as analytics_blp
from .routes.uploads import blp as uploads_blp
from .routes.public_uploads import blp as public_uploads_blp
from .utils.flask_error_handlers import register_error_handlers

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(Config)

# CORS
CORS(
    app,
    resources={r"/*": {"origins": app.config.get("ALLOWED_ORIGINS", "*").split(",")}},
    allow_headers=app.config.get("ALLOWED_HEADERS", "Content-Type,Authorization").split(","),
    methods=app.config.get("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS").split(","),
)

# OpenAPI
app.config["API_TITLE"] = app.config.get("API_TITLE", "Manufacturing Defect Management API")
app.config["API_VERSION"] = app.config.get("API_VERSION", "v1")
app.config["OPENAPI_VERSION"] = app.config.get("OPENAPI_VERSION", "3.0.3")
app.config["OPENAPI_URL_PREFIX"] = app.config.get("OPENAPI_URL_PREFIX", "/docs")
app.config["OPENAPI_SWAGGER_UI_PATH"] = app.config.get("OPENAPI_SWAGGER_UI_PATH", "")
app.config["OPENAPI_SWAGGER_UI_URL"] = app.config.get(
    "OPENAPI_SWAGGER_UI_URL", "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
)

api = Api(app)

# Error handlers
register_error_handlers(app)

# Routes
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(defects_blp)
api.register_blueprint(actions_blp)
api.register_blueprint(dashboard_blp)
api.register_blueprint(analytics_blp)
api.register_blueprint(uploads_blp)
api.register_blueprint(public_uploads_blp)
