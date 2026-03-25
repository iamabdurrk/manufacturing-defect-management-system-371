from marshmallow import Schema, fields, validate


class SignupSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6, max=200))
    role = fields.String(required=True, validate=validate.OneOf(["quality_engineer", "supervisor", "admin"]))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class AuthResponseSchema(Schema):
    token = fields.String(required=True)
    user = fields.Dict(required=True)
