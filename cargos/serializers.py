"""
Cargos serializers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


from marshmallow import Schema, fields, post_dump


class CargoSchema(Schema):
    """Serializer for Cargos model."""

    # required fields
    description = fields.Str(required=True, allow_none=False)
    size = fields.Int(required=True)

    # not-required fields
    repository = fields.Str()
    name = fields.Str(dump_only=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")

    # export only
    id = fields.Int(dump_only=True)
    cargo_id = fields.Int(dump_only=True)
    subdomain = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    specs = fields.Raw()

    @post_dump
    def owner(self, data):
        if 'user' in self.context:
            if "user_id" in data and data['user_id'] == self.context['user']:
                data['owner'] = "You"
        return data


class CargoForProbeSchema(Schema):
    text = fields.Str(attribute="volume_name")
    value = fields.Int(attribute="id")
