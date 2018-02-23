"""Cargos' events."""

import logging
from secrets import token_urlsafe

from rampante import streaming, subscribe_on

from cargos.models import mCargo
from spawner import Spawner
from utils import naminator, query_db

log = logging.getLogger(__name__)


@subscribe_on("service.cargo.create")
async def create_cargo(queue, event, app):
    """Create a new cargo."""
    log.info(f"Event: {event}")

    user_id = event["user_id"]
    cargo = event["data"]

    access_key = token_urlsafe(15).upper()
    secret_key = token_urlsafe(30)

    specs = {
        "uuid": event['uuid'],
        "access_key": access_key,
        "secret_key": secret_key,
        "description": cargo['description'],
        "size": cargo.get("size", 10),
        "cpu": 0.25,
        "ram": 0.5,
    }

    name = naminator("cargo")

    query = mCargo.insert().values(
        uuid=event['uuid'],
        user_id=user_id,
        name=name,
        specs=specs,
    )
    await query_db(app['db'], query, get_result=False)

    service = await Spawner.cargo.create(
        name=name,
        user_id=user_id,
        specs=specs,
        access_key=access_key,
        secret_key=secret_key,
    )

    if not service:
        log.error(
            f"{event['uuid']}: blueprint `{cargo['blueprint_id']}` not found")
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
