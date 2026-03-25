from marshmallow import Schema, fields


class ParetoQuerySchema(Schema):
    start = fields.String(required=False)
    end = fields.String(required=False)


class TrendsQuerySchema(Schema):
    start = fields.String(required=False)
    end = fields.String(required=False)
    interval = fields.String(required=False)  # day|week
    production_line = fields.String(required=False)
    part_number = fields.String(required=False)
    defect_type_id = fields.String(required=False)
