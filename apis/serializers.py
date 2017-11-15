"""
APIs serializers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from marshmallow import Schema, fields, post_dump

from config import Config as C


class APIs(Schema):
    """Serializer for API model."""

    # required fields
    blueprint_id = fields.Int(required=True)
    machine_type = fields.Int(required=True)
    description = fields.Str(required=True, allow_none=False)
    cargo_id = fields.Int(required=True)

    # not-required fields
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")

    # export only
    id = fields.Int(dump_only=True)
    subdomain = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    blueprint_name = fields.Str(dump_only=True)
    blueprint_repository = fields.Str(dump_only=True)

    @post_dump
    def active(self, data):
        data['running'] = False
        if data['subdomain']:
            data['running'] = True

    @post_dump
    def url(self, data):
        data['url'] = C.APPS_PUBLIC_URL.format(subdomain=data['name'])
