from flask_smorest import Blueprint
from flask.views import MethodView

from app.schemas.auth import AuthResponseSchema, LoginSchema, SignupSchema
from app.services.auth_service import AuthService

blp = Blueprint("Auth", "auth", url_prefix="/api/auth", description="Authentication routes")


@blp.route("/signup")
class Signup(MethodView):
    """User signup: creates account and returns JWT."""

    @blp.arguments(SignupSchema)
    @blp.response(200, AuthResponseSchema)
    def post(self, payload):
        svc = AuthService()
        return svc.signup(**payload)


@blp.route("/login")
class Login(MethodView):
    """User login: returns JWT."""

    @blp.arguments(LoginSchema)
    @blp.response(200, AuthResponseSchema)
    def post(self, payload):
        svc = AuthService()
        return svc.login(**payload)
