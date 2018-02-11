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
    log.info(f"{event['uuid']}: {event}")

    user_id = event["user_id"]
    api = event["data"]

    blueprint = await get_blueprint(app['db'], blueprint_uuid=api['blueprint'], user_id=user_id)

    if blueprint is None:
        log.info(
            f"{event['uuid']}: blueprint `{api['blueprint_id']}` not found")

        event = {
            "user_id": user_id,
            "message": {
                "status": "error",
                "message": "",  # TODO put a message here
            }
        }

        await streaming.publish("user.notification", event)

    name = naminator("api")

    specs = {
        'repository': blueprint.repository,
        'blueprint': f"{blueprint.name}:{blueprint.tag}",
        'networks': ["cassiny-public"],
        'machine_type': api['machine_type'],
        'command': api['command'],
        'gpu': api['gpu'],
        'premptible': api['premptible']
    }

    query = mApi.insert().values(
        uuid=event['uuid'],
        user_id=user_id,
        blueprint_id=blueprint.id,
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
            f"{event['uuid']}: blueprint `{api['blueprint_id']}` not found")
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

    log.info(f"{event['uuid']}: service.api.completed.")
    await streaming.publish("user.notification", event)
