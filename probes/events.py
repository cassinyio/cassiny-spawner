"""Probes' events."""

import logging
from secrets import token_urlsafe

from rampante import streaming, subscribe_on

from blueprints.models import get_blueprint
from probes.models import delete_probe, mProbe
from spawner import Spawner
from utils import naminator, query_db

log = logging.getLogger(__name__)


@subscribe_on("service.probe.create")
async def create_probe(queue, event, app):
    """Create a new probe."""
    user_id = event["user_id"]
    probe = event["data"]
    uuid = event["uuid"]

    blueprint = await get_blueprint(app['db'], blueprint_ref=probe['blueprint'], user_id=user_id)

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
        return

    name = naminator("probe")
    token = token_urlsafe(30)

    specs = {
        'uuid': uuid,
        'repository': blueprint.repository,
        'blueprint': f"{blueprint.name}:{blueprint.tag}",
        'networks': ["cassiny-public"],
        'machine_type': probe['machine_type'],
        'gpu': probe['gpu'],
        'preemptible': probe['preemptible']
    }

    query = mProbe.insert().values(
        uuid=uuid,
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
        log.error(f"Probe({uuid}) failed, deleting db entry.")

        await delete_probe(db=app['db'], probe_ref=uuid, user_id=user_id)
        log.info(f"DB entry for probe({uuid}) deleted.")

        event = {
            "user_id": user_id,
            "uuid": uuid,
            "data": {
                "status": "error",
                "message": "The creation of your probe failed.",
            }
        }

        await streaming.publish("user.notification", event)
        return

    event = {
        "user_id": user_id,
        "uuid": uuid,
        "name": name,
        "specs": specs
    }

    await streaming.publish("service.probe.completed", event)
