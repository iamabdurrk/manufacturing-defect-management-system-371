"""Defects and RCA validation schemas."""

from __future__ import annotations

from marshmallow import Schema, fields, validate

SEVERITY_ENUM = ["Critical", "Major", "Minor"]
RCA_METHOD_ENUM = ["5WHY", "FISHBONE"]
ACTION_STATUS_ENUM = ["Open", "In Progress", "Complete"]


class DefectCreateSchema(Schema):
    part_number = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    defect_type_id = fields.Str(required=True, validate=validate.Length(min=1))
    quantity_affected = fields.Int(required=True, validate=validate.Range(min=1))
    production_line = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    shift = fields.Str(required=True, validate=validate.Length(min=1, max=40))
    severity = fields.Str(required=False, validate=validate.OneOf(SEVERITY_ENUM))
    status = fields.Str(required=False)
    photo_file_id = fields.Str(required=False, allow_none=True)


class DefectUpdateSchema(Schema):
    part_number = fields.Str(required=False, validate=validate.Length(min=1, max=120))
    defect_type_id = fields.Str(required=False, validate=validate.Length(min=1))
    quantity_affected = fields.Int(required=False, validate=validate.Range(min=1))
    production_line = fields.Str(required=False, validate=validate.Length(min=1, max=120))
    shift = fields.Str(required=False, validate=validate.Length(min=1, max=40))
    severity = fields.Str(required=False, validate=validate.OneOf(SEVERITY_ENUM))
    status = fields.Str(required=False, validate=validate.Length(min=1, max=80))


class RootCauseUpsertSchema(Schema):
    method = fields.Str(required=True, validate=validate.OneOf(RCA_METHOD_ENUM))
    five_whys = fields.List(fields.Str(), required=False)
    fishbone = fields.Dict(required=False)


class CorrectiveActionCreateSchema(Schema):
    defect_id = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    owner_id = fields.Str(required=True, validate=validate.Length(min=1))
    due_date = fields.Str(required=True, validate=validate.Length(min=1))
    status = fields.Str(required=False, validate=validate.OneOf(ACTION_STATUS_ENUM))


class CorrectiveActionUpdateSchema(Schema):
    description = fields.Str(required=False, validate=validate.Length(min=1, max=500))
    owner_id = fields.Str(required=False, validate=validate.Length(min=1))
    due_date = fields.Str(required=False, validate=validate.Length(min=1))
    status = fields.Str(required=False, validate=validate.OneOf(ACTION_STATUS_ENUM))
    completed_date = fields.Str(required=False, allow_none=True)
