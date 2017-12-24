"""
Probes serializers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


from marshmallow import Schema, fields, post_dump
from marshmallow.validate import OneOf

from config import Config as C


class ProbeSchema(Schema):
    """Serializer for Probe model."""

    # required fields
    description = fields.Str(required=True, allow_none=False)
    blueprint_id = fields.Int(required=True)
    machine_type = fields.Str(required=True, validate=OneOf(C.SIZE))

    # export only
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(format="%Y-%m-%d")
    user_id = fields.Int(dump_only=True)
    blueprint_name = fields.Int(dump_only=True)
    blueprint_repository = fields.Str(dump_only=True)
    status = fields.Int(dump_only=True)

    @post_dump
    def owner(self, data):
        if "user_id" in data and data['user_id'] == self.context['user']:
            data['owner'] = "You"

    @post_dump
    def create_blueprint_name(self, data):
        if "blueprint_repository" in data and "blueprint_name" in data:
            repository = data['blueprint_repository']
            name = data['blueprint_name']
            data['blueprint'] = f"{repository}/{name}"

    @post_dump
    def url(self, data):
        if "url" in data:
            data['url'] = C.APPS_PUBLIC_URL.format(subdomain=data['name'])
