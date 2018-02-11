"""
Probes serializers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


from marshmallow import Schema, fields, post_dump

from config import Config as C


class ProbeSchema(Schema):
    """Serializer for Probe model."""

    # required fields
    description = fields.Str(required=True, allow_none=False)
    blueprint = fields.Str(required=True)
    machine_type = fields.Str(required=True)

    # export only
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    token = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format="%Y-%m-%d")
    user_id = fields.Int(dump_only=True)
    blueprint_name = fields.Str(dump_only=True)
    blueprint_repository = fields.Str(dump_only=True)
    status = fields.Int(dump_only=True)
    specs = fields.Raw()

    @post_dump
    def owner(self, data):
        if "user_id" in data and data['user_id'] == self.context['user']:
            data['owner'] = "You"

    @post_dump
    def translate_status(self, data):
        data['status'] = C.STATUS[data['status']]

    @post_dump
    def create_blueprint_name(self, data):
        if "blueprint_repository" in data and "blueprint_name" in data:
            repository = data['blueprint_repository']
            name = data['blueprint_name']
            data['blueprint'] = f"{repository}/{name}"

    @post_dump
    def url(self, data):
        data['url'] = C.APPS_PUBLIC_URL.format(subdomain=data['name'])
