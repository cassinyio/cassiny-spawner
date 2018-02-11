"""
APIs serializers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from marshmallow import Schema, fields, post_dump

from config import Config as C


class APIs(Schema):
    """Serializer for APIs model."""

    # required fields
    description = fields.Str(required=True, allow_none=False)
    blueprint_id = fields.Int(required=True)
    machine_type = fields.Str(required=True)
    command = fields.Str(required=True, allow_none=False)
    gpu = fields.Bool(required=True, allow_none=False)
    premptible = fields.Bool(required=True, allow_none=False)

    # not-required fields
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")

    # export only
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    blueprint_name = fields.Str(dump_only=True)
    blueprint_repository = fields.Str(dump_only=True)
    status = fields.Int(dump_only=True)
    specs = fields.Raw()

    @post_dump
    def translate_status(self, data):
        data['status'] = C.STATUS[data['status']]

    @post_dump
    def url(self, data):
        data['url'] = C.APPS_PUBLIC_URL.format(subdomain=data['name'])
