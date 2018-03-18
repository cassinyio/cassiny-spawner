"""APIs' events."""

import logging

from rampante import streaming, subscribe_on

from apis.models import mApi
from blueprints.models import get_blueprint
from spawner import Spawner
from utils import naminator, query_db

log = logging.getLogger(__name__)


@subscribe_on("service.api.create")
async def create_api(queue, event, app):
    """"""
    user_id = event["user_id"]
    api = event["data"]
    uuid = event["uuid"]

    blueprint = await get_blueprint(app['db'], blueprint_ref=api['blueprint'], user_id=user_id)

    if blueprint is None:
        log.info(
            f"{uuid}: blueprint `{api['blueprint']}` not found")

        event = {
            "user_id": user_id,
            "message": {
                "status": "error",
                "message": "",  # TODO put a message here
            }
        }

        await streaming.publish("user.notification", event)
        return

    name = naminator("api")

    specs = {
        'uuid': uuid,
        'repository': blueprint.repository,
        'blueprint': f"{blueprint.name}:{blueprint.tag}",
        'networks': ["cassiny-public"],
        'machine_type': api['machine_type'],
        'command': api['command'],
        'gpu': api['gpu'],
        'preemptible': api['preemptible']
    }

    query = mApi.insert().values(
        uuid=uuid,
        user_id=user_id,
        blueprint_uuid=blueprint.uuid,
        name=name,
        description=api['description'],
        specs=specs,
    )
    await query_db(app['db'], query, get_result=False)

    service = await Spawner.api.create(
        name=name,
        user_id=user_id,
        specs=specs
    )

    # docker events is in charge of updating status
    if not service:
        log.error(
            f"{uuid}: blueprint `{api['blueprint_uuid']}` not found")
        event = {
            "user_id": user_id,
            "message": {
                "status": "error",
                "message": "",  # TODO put a message here
            }
        }

        await streaming.publish("user.notification", event)
        return

    notifcation = {
        "user_id": user_id,
        "message": {
            "status": "error",
            "message": "",  # TODO put a message here
        }
    }
    await streaming.publish("user.notification", notifcation)
    log.info(f"{event['uuid']}: service.api.completed.")
