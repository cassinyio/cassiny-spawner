"""Probes' events."""

import logging
from secrets import token_urlsafe

from rampante import streaming, subscribe_on

from blueprints.models import get_blueprint
from probes.models import mProbe
from spawner import Spawner
from utils import naminator, query_db

log = logging.getLogger(__name__)


@subscribe_on("service.probe.create")
async def create_probe(queue, event, app):
    """Create a new probe."""
    log.info(f"Event: {event}")

    user_id = event["user_id"]
    probe = event["data"]

    blueprint = await get_blueprint(app['db'], blueprint_uuid=probe['blueprint'], user_id=user_id)

    if blueprint is None:
        log.info(
            f"{event['uuid']}: blueprint `{probe['blueprint']}` not found."
        )

        event = {
            "user_id": user_id,
            "message": {
                "status": "error",
                "message": "",  # TODO put a message here
            }
        }

        await streaming.publish("user.notification", event)

    name = naminator("probe")
    token = token_urlsafe(30)

    specs = {
        'uuid': event['uuid'],
        'repository': blueprint.repository,
        'blueprint': f"{blueprint.name}:{blueprint.tag}",
        'networks': ["cassiny-public"],
        'machine_type': probe['machine_type'],
        'gpu': probe['gpu'],
        'preemptible': probe['preemptible']
    }

    query = mProbe.insert().values(
        uuid=event['uuid'],
        user_id=user_id,
        blueprint_uuid=blueprint.uuid,
        name=name,
        token=token,
        description=probe['description'],
        specs=specs,
    )
    await query_db(app['db'], query, get_result=False)

    service = await Spawner.probe.create(
        name=name,
        user_id=user_id,
        specs=specs,
        token=token,
    )

    if not service:
        log.error(
            f"{event['uuid']}: blueprint `{probe['blueprint']}` not found")
        event = {
            "user_id": user_id,
            "message": {
                "status": "error",
                "message": "",  # TODO put a message here
            }
        }
        await streaming.publish("user.notification", event)

    event = {
        "user_id": user_id,
        "message": {
            "status": "error",
            "message": "",  # TODO put a message here
        }
    }

    log.info(f"{event['uuid']}: service.job.completed.")
    await streaming.publish("user.notification", event)
