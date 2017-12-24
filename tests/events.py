import asyncio
from types import MappingProxyType
from unittest.mock import patch

import msgpack


async def _validate_token(*args):
    """Trick the _validate token to return 1."""
    return MappingProxyType({"user_id": 1})

patch('utils.auth._validate_token', _validate_token).start()

EVENTS = []
# 50 service * 2 event received
SERVICES = 20
CORRECT_SERVICES = SERVICES * 2
COUNTING_FROM = 1000


async def _send_event(*args, **kwargs):
    global EMAILS_SENT
    """Count number of sent emails."""
    body = msgpack.packb(kwargs['message'])
    EVENTS.append(msgpack.unpackb(body, encoding='utf-8'))

patch('events.watcher._send_event', _send_event).start()


async def test_create_service(cli, docker):

    TaskTemplate = {
        "ContainerSpec": {
            "Image": "redis",
            "Labels": {
                "user_id": "1",
            }
        },
    }

    services = []
    # we expect 4 chars for the number part
    for i in range(COUNTING_FROM, COUNTING_FROM + SERVICES):
        service = await docker.services.create(
            task_template=TaskTemplate,
            name=f"probe-pincopallo-{i}"
        )
        services.append(service['ID'])

    # wait a bit to spawn the services
    await asyncio.sleep(10)
    for service in services:
        await docker.services.delete(service)
    # wait until all the services are removed
    await asyncio.sleep(10)
    await docker.swarm.leave(force=True)
    for event in EVENTS:
        assert 'msg_type' in event
    assert len(EVENTS) == CORRECT_SERVICES


async def test_create_wrong_service(cli, docker):

    TaskTemplate = {
        "ContainerSpec": {
            "Image": "redis",
        },
    }

    service = await docker.services.create(
        task_template=TaskTemplate,
        name="pincopallo-8989"
    )
    await asyncio.sleep(10)
    await docker.services.delete(service['ID'])
    await asyncio.sleep(10)
    await docker.swarm.leave(force=True)
    assert len(EVENTS) == CORRECT_SERVICES
