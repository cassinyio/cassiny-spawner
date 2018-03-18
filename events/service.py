import logging
import re
from typing import Mapping, Optional

import msgpack

from config import Status
from events.models import mLog
from utils import query_db

log = logging.getLogger(__name__)

TOPIC_NAME = 'user.notification'
REGEX = re.compile('([a-z]+)-[a-z]+-[0-9]{4}$')


class validate_docker_event:
    def __init__(self, event: Mapping):
        self.event = event

    def __enter__(self):
        if is_container_event(self.event):
            dockerlog = DockerEvent().from_event(event=self.event)
            if dockerlog.user_id and dockerlog.service_type is not None:
                return dockerlog
        return False

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def is_container_event(event: Mapping) -> bool:
    """Return true if the event is a container event."""
    if event['Type'] == 'container':
        if event['Action'] in ("create", "start", "die", "destroy"):
            return True
    return False


def get_service_type(name: str) -> Optional[str]:
    """Return type of a service, None if don't match."""
    try:
        return REGEX.match(name)[1]
    except TypeError:
        return None


def get_service_status(service_type: str, action: str, exit_code: str):
    """Return `False` or the current status for a service."""
    if service_type in ("probe", "cargo", "api"):
        if action == 'start':
            return Status.Running
        if action == 'destroy':
            return Status.Stopped

    if service_type == "job":
        if action == 'start':
            return Status.Running
        if action == 'die':
            if exit_code == '1':
                return Status.Failed
            return Status.Completed

    return False


def prepare_message(log):
    """Check if a message has to be sent."""
    # send messages only for started and destroyed services
    if log.action in ("start", "destroy"):
        if log.action == "start":
            msg = "created"
            text = "has been created"

        if log.action == "destroy":
            msg = "destroyed"
            text = "has been destroyed"

        ws_msg = {
            'user_id': log.user_id,
            'msg_type': log.service_type,
            'title': f"{log.name} {msg}",
            'text': f"Your {log.service_type} {text}",
            'timestamp': log.time
        }
        return ws_msg
    return None


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
        self.service_type = get_service_type(self.name)

        return self

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


async def add_log(db, log) -> None:
    """Add a new log for services events."""
    query = mLog.insert().values(
        uuid=log.uuid,
        log_type=log.type,
        service_type=log.service_type,
        name=log.name,
        action=log.action,
        user_id=log.user_id
    )
    await query_db(db, query, get_result=False)


async def update_service_status(db, model, log: DockerEvent) -> None:
    """Update status for a docker event."""
    status = get_service_status(log.service_type, log.action, log.exit_code)

    if status:
        query = model.update()\
            .where(model.c.name == log.name)\
            .values(
            status=status.value,
        )
        await query_db(db, query, get_result=False)
