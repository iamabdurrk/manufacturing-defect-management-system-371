from marshmallow import Schema, fields


class UploadResponseSchema(Schema):
    file_id = fields.String(required=True)
    filename = fields.String(required=True)
    content_type = fields.String(required=True)
    size = fields.Integer(required=True)
    url = fields.String(required=True)
