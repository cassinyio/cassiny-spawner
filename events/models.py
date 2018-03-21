"""
Logs models.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import re
from typing import Mapping, Optional

import msgpack
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from factory import metadata

REGEX = re.compile('([a-z]+)-[a-z]+-[0-9]{4}$')

mLog = Table(
    'logs',
    metadata,
    Column('id', Integer, primary_key=True),
    # unique log identifier
    Column('uuid', UUID),
    Column('log_type', String(10)),
    Column('service_type', String(5)),
    Column('name', String(200)),
    Column('action', String(10)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('user_id', Integer, nullable=False),

    # uuid-action should be unique
    UniqueConstraint('uuid', 'action'),
)


class DockerEvent():
    """Class to handle docker events."""

    _keys = frozenset((
        "action",
        "type",
        "time",
        "name",
        "user_id",
        "service_type",
        "uuid",
        "exit_code",
    ))

    # Attributes we want to take from the docker event
    _attributes = frozenset((
        "com.docker.swarm.service.name",
        "user_id",
        "uuid",
        "service_type",
        "exitCode",
    ))

    def __init__(self) -> None:
        self.action = None
        self.type = None
        self.time = None
        self.uuid = None
        self.name = None
        self.user_id = None
        self.exit_code = None
        self.service_type: str = None

    def from_event(self, *, event: Mapping):
        if "Actor" in event and "Attributes" in event["Actor"]:
            self._pack_attrs(event_attrs=event["Actor"]["Attributes"])

        self.action = event['Action']
        self.type = event['Type']
        self.time = event['time'].strftime("%d/%m/%Y %H:%M:%S")
        self.service_type = self.get_service_type(self.name)

        return self

    @staticmethod
    def get_service_type(name) -> Optional[str]:
        """Return type of a service, None if don't match."""
        try:
            return REGEX.match(name)[1]
        except TypeError:
            return None

    def _pack_attrs(self, *, event_attrs: Mapping):
        """Take only the valid attrs from a docker event log."""
        for key in self._attributes & event_attrs.keys():
            if key == 'exitCode':
                self.__dict__['exit_code'] = event_attrs[key]
            elif key == 'com.docker.swarm.service.name':
                self.__dict__['name'] = event_attrs[key]
            elif key == 'user_id':
                self.__dict__[key] = int(event_attrs[key])
            elif key == 'uuid':
                self.__dict__[key] = event_attrs[key]

    def to_dict(self):
        return {key: self.__dict__[key] for key in self._keys & self.__dict__.keys()}

    def unpack(self, *, message):
        msg_unpacked = msgpack.unpackb(
            message, use_list=False, encoding='utf-8')
        for key in self._keys & msg_unpacked.keys():
            self.__dict__[key] = msg_unpacked[key]
        return self
