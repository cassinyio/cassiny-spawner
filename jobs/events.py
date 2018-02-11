"""Jobs' events."""

import logging

from rampante import streaming, subscribe_on

from blueprints.models import get_blueprint
from jobs.models import mJob
from spawner import Spawner
from utils import naminator, query_db

log = logging.getLogger(__name__)


@subscribe_on("service.job.create")
async def create_job(queue, event, app):
    """Create a new job."""
    log.info(f"{event['uuid']}: {event}")

    user_id = event["user_id"]
    job = event["data"]

    blueprint = await get_blueprint(app['db'], blueprint_uuid=job['blueprint'], user_id=user_id)

    if blueprint is None:
        log.info(
            f"{event['uuid']}: blueprint `{job['blueprint_id']}` not found")

        event = {
            "user_id": user_id,
            "message": {
                "status": "error",
                "message": "",  # TODO put a message here
            }
        }

        await streaming.publish("user.notification", event)

    name = naminator("job")

    specs = {
        'repository': blueprint.repository,
        'blueprint': f"{blueprint.name}:{blueprint.tag}",
        'networks': ["cassiny-public"],
        'machine_type': job['machine_type'],
        'command': job['command'],
        'gpu': job['gpu'],
        'premptible': job['premptible']
    }

    query = mJob.insert().values(
        uuid=event['uuid'],
        user_id=user_id,
        blueprint_id=blueprint.id,
        name=name,
        description=job['description'],
        specs=specs,
    )
    await query_db(app['db'], query, get_result=False)

    service = await Spawner.job.create(
        name=name,
        user_id=user_id,
        specs=specs,
    )

    if not service:
        log.error(
            f"{event['uuid']}: blueprint `{job['blueprint_id']}` not found")
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
