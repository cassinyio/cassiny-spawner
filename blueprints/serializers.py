"""
Blueprints serializers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


from marshmallow import Schema, fields


class BlueprintForProbeSchema(Schema):
    value = fields.Int(attribute="id")
    text = fields.Str(attribute="name")


class CreateBlueprint(Schema):
    name = fields.Str(required=True)
    tag = fields.Str(required=True)
    base_image = fields.Str(required=True)
    description = fields.Str(required=True)


class CreateBlueprintFromCargo(Schema):
    name = fields.Str(required=True)
    tag = fields.Str(required=True)
    base_image = fields.Str(required=True)
    description = fields.Str(required=True)
    cargo = fields.Str(required=True)
    bucket = fields.Str(required=True)


class BlueprintSchema(Schema):
    uuid = fields.Str()
    repository = fields.Str()
    name = fields.Str()
    tag = fields.Str()
    link = fields.Str()
    description = fields.Str()
    public = fields.Bool()
    created_at = fields.DateTime(format="%Y-%m-%d")
