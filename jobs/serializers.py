"""
Jobs serializers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from marshmallow import Schema, fields, post_dump
from marshmallow.validate import OneOf

from config import Config, Status


class JobSchema(Schema):
    """Serializer for Jobs model."""

    # required fields
    description = fields.Str(required=True, allow_none=False)
    blueprint = fields.Str(required=True)
    machine_type = fields.Str(required=True, validate=OneOf(Config.MACHINES))
    command = fields.Str(required=True, allow_none=False)
    gpu = fields.Bool(required=True, allow_none=False)
    preemptible = fields.Bool(required=True, allow_none=False)

    # export only
    uuid = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")

    user_id = fields.Int(dump_only=True)
    blueprint_name = fields.Str(dump_only=True)
    blueprint_repository = fields.Str(dump_only=True)
    status = fields.Int(dump_only=True)
    specs = fields.Raw()

    @post_dump
    def translate_status(self, data):
        data['status'] = Status(data['status']).name

    @post_dump
    def owner(self, data):
        if data['user_id'] == self.context['user']:
            data['owner'] = "You"

    @post_dump
    def create_blueprint_name(self, data):
        data['blueprint'] = "/".join((data['blueprint_repository'], data['blueprint_name']))
