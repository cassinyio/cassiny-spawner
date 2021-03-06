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
    """Task `job.create` events."""
    user_id = event["user_id"]
    job = event["data"]
    uuid = event["uuid"]

    blueprint = await get_blueprint(app['db'], blueprint_ref=job['blueprint'], user_id=user_id)

    if blueprint is None:
        log.info(
            f"{uuid}: blueprint `{job['blueprint']}` not found")

        event = {
            "user_id": user_id,
            "message": {
                "status": "error",
                "message": f"{job['blueprint']} does not exist.",
            }
        }

        await streaming.publish("user.notification", event)
        return

    name = naminator("job")

    specs = {
        'uuid': uuid,
        'repository': blueprint.repository,
        'blueprint': f"{blueprint.name}:{blueprint.tag}",
        'networks': ["cassiny-public"],
        'machine_type': job['machine_type'],
        'command': job['command'],
        'gpu': job['gpu'],
    }

    query = mJob.insert().values(
        uuid=uuid,
        user_id=user_id,
        blueprint_uuid=blueprint.uuid,
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
        log.error(f"Job({uuid}) creation failed.")
        return

    event = {
        "user_id": user_id,
        "uuid": uuid,
        "name": name,
        "specs": specs
    }

    await streaming.publish("service.job.completed", event)
