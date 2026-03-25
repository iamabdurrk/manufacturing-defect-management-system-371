import os


class Config:
    """Application configuration (env-driven)."""

    # Flask / OpenAPI
    API_TITLE = os.getenv("API_TITLE", "Manufacturing Defect Management API")
    API_VERSION = os.getenv("API_VERSION", "v1")
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/docs"
    OPENAPI_SWAGGER_UI_PATH = ""
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Base URL
    # Used to generate absolute URLs (e.g., uploads) returned to the frontend.
    # Example: https://api.example.com
    BACKEND_URL = os.getenv("BACKEND_URL", "")

    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    ALLOWED_HEADERS = os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization")
    ALLOWED_METHODS = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS")

    # MongoDB
    # NOTE: DB container provides MONGODB_URL and MONGODB_DB at runtime.
    MONGODB_URL = os.getenv("MONGODB_URL")
    MONGODB_DB = os.getenv("MONGODB_DB")

    # JWT
    # NOTE: Must be set by orchestrator in .env for production.
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ISSUER = os.getenv("JWT_ISSUER", "mdms")
    JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "mdms-web")
    JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "480"))

    # Uploads
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(15 * 1024 * 1024)))  # 15MB
    PUBLIC_UPLOADS_ROUTE = os.getenv("PUBLIC_UPLOADS_ROUTE", "/uploads")

    # App
    TRUST_PROXY = os.getenv("TRUST_PROXY", "false").lower() == "true"
