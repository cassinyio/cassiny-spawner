from marshmallow import Schema, fields


class Logs(Schema):
    id = fields.Int(dump_only=True)
    log_type = fields.Str()
    service_type = fields.Str()
    name = fields.Str()
    action = fields.Str()
    usage = fields.Float()
    created = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    destroyed = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    user_id = fields.Int(dump_only=True)
