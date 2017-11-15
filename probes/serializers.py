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
    blueprint_id = fields.Int(required=True)
    machine_type = fields.Int(required=True)

    # not-required fields
    cargo_id = fields.Int(required=False)

    # export only
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(format="%Y-%m-%d")
    user_id = fields.Int(dump_only=True)
    blueprint_name = fields.Int(dump_only=True)
    blueprint_repository = fields.Str(dump_only=True)
    subdomain = fields.Str(dump_only=True)

    @post_dump
    def owner(self, data):
        if data['user_id'] == self.context['user']:
            data['owner'] = "You"

    @post_dump
    def active(self, data):
        data['running'] = False
        if data['subdomain']:
            data['running'] = True

    @post_dump
    def create_blueprint_name(self, data):
        data['blueprint'] = "/".join((data['blueprint_repository'], data['blueprint_name']))

    @post_dump
    def url(self, data):
        data['url'] = C.APPS_PUBLIC_URL.format(subdomain=data['name'])
