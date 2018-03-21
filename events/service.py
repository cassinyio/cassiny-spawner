import logging
from typing import Mapping, Optional

from config import Status
from events.models import DockerEvent, mLog
from utils import query_db

log = logging.getLogger(__name__)

TOPIC_NAME = 'user.notification'


class validate_docker_event:
    def __init__(self, event: Mapping) -> None:
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


def prepare_message(log: DockerEvent) -> Optional[Mapping]:
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
