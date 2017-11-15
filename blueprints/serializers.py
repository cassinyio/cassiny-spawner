"""
    serializers.py
    ~~~~~~~~~
    Blueprints Schema model

    :copyright: (c) 2017, Cassiny.io OÜ.
    All rights reserved.
"""


from marshmallow import Schema, fields


class BlueprintForProbeSchema(Schema):
    value = fields.Int(attribute="id")
    text = fields.Str(attribute="name")


class BlueprintSchema(Schema):
    id = fields.Int()
    repository = fields.Str()
    name = fields.Str()
    tag = fields.Str()
    link = fields.Str()
    description = fields.Str()
    public = fields.Bool()
    created_at = fields.DateTime(format="%Y-%m-%d")
