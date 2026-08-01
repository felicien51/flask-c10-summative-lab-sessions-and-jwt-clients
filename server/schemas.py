from marshmallow import Schema, fields, validate


class SignUpSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1, max=80))
    password = fields.String(required=True, validate=validate.Length(min=6))
    password_confirmation = fields.String(required=True)


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class TaskSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False, allow_none=True)
    priority = fields.String(
        required=False, validate=validate.OneOf(["low", "medium", "high"])
    )
    completed = fields.Boolean(required=False)
    due_date = fields.Date(required=False, allow_none=True)


class TaskUpdateSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False, allow_none=True)
    priority = fields.String(
        required=False, validate=validate.OneOf(["low", "medium", "high"])
    )
    completed = fields.Boolean(required=False)
    due_date = fields.Date(required=False, allow_none=True)
