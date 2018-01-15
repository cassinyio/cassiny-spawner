import asyncio
import logging
import re
from typing import Optional

from rampante import streaming

from apis import mApi
from cargos import mCargo
from events.models import mLog
from events.utils import DockerEvent
from jobs import mJob
from probes import mProbe

MODEL_TYPE = {
    "probe": mProbe,
    "api": mApi,
    "cargo": mCargo,
    "job": mJob,
}


log = logging.getLogger(__name__)

TOPIC_NAME = 'user.notification'
REGEX = re.compile('([a-z]+)-[a-z]+-[0-9]{4}$')


def get_service_type(name: str) -> Optional[str]:
    """Return type of a service, None if don't match."""
    try:
        return REGEX.match(name)[1]
    except TypeError:
        return None


def get_service_status(service_type, action):
    """Return `False` or the current status for a service."""
    if service_type in ("probe", "cargo", "api"):
        if action == 'start':
            return 1
        if action == 'destroy':
            return 4
    if service_type == "job":
        if action == 'start':
            return 1
        if action == 'die':
            return 2
    return False


def prepare_message(log, service_type):
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
            'msg_type': service_type,
            'title': f"{log.name} {msg}",
            'text': f"Your {service_type} {text}",
            'timestamp': log.time
        }
        return ws_msg
    return None


async def docker_listener(app):
    """Docker events listener."""
    log.info("Docker watcher started")
    subscriber = app['docker'].events.subscribe()
    try:
        while True:
            event = await subscriber.get()

            if event is None:
                break

            actions = ("create", "start", "die", "destroy")

            if event['Type'] == 'container' and event['Action'] in actions:
                docker_log = DockerEvent().pack(event=event)

                service_type = get_service_type(docker_log.name)

                if docker_log.user_id and service_type is not None:

                    log.info(docker_log.to_dict())

                    model = MODEL_TYPE[service_type]

                    async with app["db"].acquire() as conn:
                        query = mLog.insert().values(
                            uuid=docker_log.log_uuid,
                            log_type=docker_log.type,
                            service_type=service_type,
                            name=docker_log.name,
                            action=docker_log.action,
                            user_id=docker_log.user_id
                        )
                        await conn.execute(query)

                        status = get_service_status(service_type, docker_log.action)

                        if status:
                            query = model.update()\
                                .where(model.c.name == docker_log.name)\
                                .values(
                                status=status,
                            )
                            await conn.execute(query)

                    message = prepare_message(docker_log, service_type)
                    if message:
                        await streaming.publish(TOPIC_NAME, message)
    except asyncio.CancelledError:
        log.info("Shutting down Docker watcher....")
