"""Auth request validation schemas."""

from __future__ import annotations

from marshmallow import Schema, fields, validate

ROLE_ENUM = ["quality_engineer", "supervisor", "admin"]


class SignupSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=200))
    role = fields.Str(required=True, validate=validate.OneOf(ROLE_ENUM))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))
