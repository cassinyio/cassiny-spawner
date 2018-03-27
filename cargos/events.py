"""Cargos' events."""

import logging
from secrets import token_urlsafe

from rampante import streaming, subscribe_on

from cargos.models import delete_cargo, mCargo
from spawner import Spawner
from utils import naminator, query_db

log = logging.getLogger(__name__)


@subscribe_on("service.cargo.create")
async def create_cargo(queue, event, app):
    """Task `cargo.create` events."""
    uuid = event['uuid']
    user_id = event["user_id"]
    cargo = event["data"]

    access_key = token_urlsafe(15).upper()
    secret_key = token_urlsafe(30)

    specs = {
        "uuid": uuid,
        "access_key": access_key,
        "secret_key": secret_key,
        "description": cargo['description'],
        "size": cargo.get("size", 10),
        "cpu": 0.25,
        "ram": 0.5,
    }

    name = naminator("cargo")

    query = mCargo.insert().values(
        uuid=uuid,
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
        log.error(f"Cargo({uuid}) creation failed, deleting db entry.")

        await delete_cargo(db=app['db'], cargo_ref=uuid, user_id=user_id)
        log.info(f"DB entry for cargo({uuid}) deleted.")

        event = {
            "user_id": user_id,
            "uuid": uuid,
            "data": {
                "status": "error",
                "message": "The creation of your cargo failed.",
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

    await streaming.publish("service.cargo.completed", event)
