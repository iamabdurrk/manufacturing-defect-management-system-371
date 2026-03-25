from marshmallow import Schema, fields, validate


class DefectCreateSchema(Schema):
    part_number = fields.String(required=True, validate=validate.Length(min=1, max=120))
    defect_type_id = fields.String(required=True)
    quantity_affected = fields.Integer(required=True, validate=validate.Range(min=1))
    production_line = fields.String(required=True, validate=validate.Length(min=1, max=120))
    shift = fields.String(required=True, validate=validate.Length(min=1, max=40))
    severity = fields.String(required=False, validate=validate.OneOf(["Critical", "Major", "Minor"]))
    status = fields.String(required=False)  # service will normalize and enforce
    photo_file_id = fields.String(required=False, allow_none=True)


class DefectUpdateSchema(Schema):
    part_number = fields.String(required=False, validate=validate.Length(min=1, max=120))
    defect_type_id = fields.String(required=False)
    quantity_affected = fields.Integer(required=False, validate=validate.Range(min=1))
    production_line = fields.String(required=False, validate=validate.Length(min=1, max=120))
    shift = fields.String(required=False, validate=validate.Length(min=1, max=40))
    severity = fields.String(required=False, validate=validate.OneOf(["Critical", "Major", "Minor"]))
    status = fields.String(required=False, validate=validate.Length(min=1, max=80))


class DefectTypeSchema(Schema):
    code = fields.String(required=True, validate=validate.Length(min=1, max=80))
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(required=False, allow_none=True)
    is_active = fields.Boolean(required=False, load_default=True)


class RootCauseUpsertSchema(Schema):
    method = fields.String(required=True, validate=validate.OneOf(["5WHY", "FISHBONE"]))
    five_whys = fields.List(fields.String(), required=False)  # ordered list
    fishbone = fields.Dict(required=False)  # {category: [items]}


class CorrectiveActionCreateSchema(Schema):
    defect_id = fields.String(required=True)
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    owner_id = fields.String(required=True)
    due_date = fields.String(required=True)  # ISO date expected
    status = fields.String(required=False, validate=validate.OneOf(["Open", "In Progress", "Complete"]))


class CorrectiveActionUpdateSchema(Schema):
    description = fields.String(required=False, validate=validate.Length(min=1, max=500))
    owner_id = fields.String(required=False)
    due_date = fields.String(required=False)
    status = fields.String(required=False, validate=validate.OneOf(["Open", "In Progress", "Complete"]))
    completed_date = fields.String(required=False, allow_none=True)


class SeverityRuleSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    # Store a small JSON-like condition blob; service interprets it.
    condition = fields.Dict(required=True)
    severity = fields.String(required=True, validate=validate.OneOf(["Critical", "Major", "Minor"]))
