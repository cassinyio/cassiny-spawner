"""
Responsible for executing jobs on the worker.

=============
:mod:`worker`
=============
"""

import logging
from secrets import token_urlsafe
from typing import Dict

from rampante import streaming, subscribe_on
from sqlalchemy.sql import select

from apis.models import mApi
from blueprints.models import mBlueprint
from cargos.models import mCargo, mSpaceDock
from jobs.models import mJob
from probes.models import mProbe
from spawner import Spawner

log = logging.getLogger(__name__)


@subscribe_on("service.cargo.create")
async def create_cargo(queue: str, event: Dict, app) -> None:
    """Task `cargo.create` events."""
    # select the first spacedock
    # with the biggest size available

    specs = event["specs"]
    user_id = event["user_id"]

    async with app['db'].acquire() as conn:
        query = mSpaceDock.select().where(
            mSpaceDock.c.size > event['size'],
        ).\
            order_by(mSpaceDock.c.size.desc())
        result = await conn.execute(query)
        spacedock = await result.fetchone()

    if spacedock is None:
        log.error("It seems we are running out of spacedocks!")
        message = "It seems we cannot create your cargo right now :("
        event = {
            "user_id": event['user_id'],
            "message": message
        }
        await streaming.publish("user.websocket", event)
        return

    access_key = token_urlsafe(15).upper()
    secret_key = token_urlsafe(30)

    async with app['db'].acquire() as conn:
        query = mCargo.insert().values(
            name=event['name'],
            description=event['description'],
            size=event['size'],
            spacedock_id=spacedock.id,
            user_id=event['user_id'],
            access_key=access_key,
            secret_key=secret_key,
        )
        await conn.execute(query)

    # specs are passed to the spawner and
    # saved inside the db
    specs.update({
        'args': "server /data",
        'repository': "minio",
        'blueprint': "minio:RELEASE.2017-08-05T00-00-53Z",
        'networks': ["probes-network"]
    })

    result = await Spawner.cargo.create(
        name=event['name'],
        user_id=user_id,
        specs=specs,
        access_key=access_key,
        secret_key=secret_key,
    )

    if result:
        message = f"Your API ({event['name']}) has been created!"
        event = {
            "user_id": event['user_id'],
            "message": message
        }
        await streaming.publish("user.websocket", event)


@subscribe_on("service.api.create")
async def create_api(queue: str, event: Dict, app):
    """Task `api.create` events."""
    specs = event["specs"]
    user_id = event["user_id"]

    query = select([mBlueprint])\
        .where(
            (mBlueprint.c.id == specs["blueprint_id"]) &
            (
                (mBlueprint.c.public.is_(True)) |
                (mBlueprint.c.user_id == user_id)
            )
    )
    async with app['db'].acquire() as conn:
        result = await conn.execute(query)
        blueprint = await result.fetchone()

    if blueprint is None:
        log.error(f"Blueprint `{specs['blueprint_id']}` does not exist or "
                  f"is not owned by user `{user_id}`"
                  )
        message = (
            "This is an error.....we cannot create your API, "
            "did you select the right blueprint?"
        )
        event = {
            "user_id": event['user_id'],
            "message": message
        }
        await streaming.publish("user.websocket", event)
        return

    cargo_id = specs['cargo_id']

    query = select([mCargo]).where(
        (mCargo.c.id == cargo_id) &
        (mCargo.c.user_id == user_id)
    )

    async with app['db'].acquire() as conn:
        result = await conn.execute(query)
        cargo = await result.fetchone()

    if cargo is None:
        log.error(f"Cargo {cargo_id} does not exist or "
                  "is a property of user `{user_id}`"
                  )
        message = (
            "This is an error.....we cannot create your API, "
            "did you select the right cargo?"
        )
        event = {
            "user_id": event['user_id'],
            "message": message
        }
        await streaming.publish("user.websocket", event)

    specs['repository'] = blueprint.repository
    specs['blueprint'] = ":".join((blueprint.name, blueprint.name))
    specs['networks'] = ["api-network"]

    log.debug(f"Creating an api with specs: {specs}")

    async with app['db'].acquire() as conn:
        query = mApi.insert().values(
            user_id=user_id,
            name=event['name'],
            blueprint_id=blueprint.id,
            cargo_id=cargo.id,
            description=specs["description"],
            specs=specs,
        )
        await conn.execute(query)

    result = await Spawner.api.create(
        name=event['name'],
        user_id=user_id,
        specs=specs
    )

    if result:
        # emit positive event
        pass
    return


@subscribe_on("service.probe.create")
async def create_probe(queue, event, app):
    """Task `probe.create` events."""
    specs = event["specs"]
    user_id = event["user_id"]

    cargo = None
    if 'cargo_id' is specs and specs['cargo_id'] is not None:
        async with app['db'].acquire() as conn:
            query = mCargo.select().where(
                (mCargo.c.user_id == user_id) &
                (mCargo.c.id == specs['cargo_id'])
            )
            result = await conn.execute(query)
            cargo = await result.fetchone()

    cargo_id = cargo.id if cargo is not None else None

    async with app['db'].acquire() as conn:
        # the blueprint has to be owned by the user
        # or has to be public
        query = mBlueprint.select().where(
            (
                mBlueprint.c.id == specs['blueprint_id']) &
            (
                (mBlueprint.c.user_id == user_id) |
                (mBlueprint.c.public.is_(True))
            )
        )
        result = await conn.execute(query)
        blueprint = await result.fetchone()

    if blueprint is None:
        log.error(f"Blueprint {specs['blueprint_id']} does not exist or "
                  f"is a property of user `{user_id}`"
                  )
        message = (
            "This is an error.....we cannot create your API, "
            "did you select the right blueprint?"
        )
        event = {
            "user_id": user_id,
            "message": message
        }
        await streaming.publish("user.websocket", event)
        return

    specs.update({
        'repository': blueprint.repository,
        'blueprint': ":".join((blueprint.name, blueprint.name)),
        'networks': ["probes-network"]
    })

    async with app['db'].acquire() as conn:
        query = mProbe.insert().values(
            user_id=user_id,
            blueprint_id=blueprint.id,
            cargo_id=cargo_id,
            name=event["name"],
            description=specs['description'],
            specs=specs,
        )
        await conn.execute(query)

    result = await Spawner.probe.create(
        name=event['name'],
        user_id=user_id,
        specs=specs,
    )

    if result:
        message = f"Your probe ({event['name']}) has been created!"
        event = {
            "user_id": event['user_id'],
            "message": message
        }
        await streaming.publish("user.websocket", event)


@subscribe_on("service.job.create")
async def create_job(queue, event, app):
    """Task `job.create` events."""
    specs = event["specs"]
    user_id = event["user_id"]

    async with app['db'].acquire() as conn:
        query = select([mBlueprint])\
            .where(
                (mBlueprint.c.id == specs["blueprint_id"]) &
                (
                    (mBlueprint.c.public.is_(True)) |
                    (mBlueprint.c.user_id == user_id)
                )
        )
        result = await conn.execute(query)
        blueprint = await result.fetchone()

    if blueprint is None:
        log.error(f"Blueprint {specs['blueprint_id']} does not exist or "
                  "is a property of user `{user_id}`"
                  )
        message = (
            "This is an error.....we cannot create your API, "
            "did you select the right blueprint?"
        )
        event = {
            "user_id": user_id,
            "message": message
        }
        await streaming.publish("user.websocket", event)
        return

    specs['repository'] = blueprint.repository
    specs['blueprint'] = ":".join((blueprint.name, blueprint.name))

    log.debug(f"Creating a job with specs: {specs}")

    # job_id returns the id of the probe just created
    async with app['db'].acquire() as conn:
        query = mJob.insert().values(
            user_id=event['user_id'],
            name=event['name'],
            blueprint_id=specs["blueprint_id"],
            cargo_id=specs["cargo_id"],
            description=specs["description"],
            specs=specs,
        )
        await conn.execute(query)

    result = await Spawner.job.create(
        name=event['name'],
        user_id=user_id,
        specs=specs,
    )

    if result:
        message = f"Your job ({event['name']}) has been created!"
        event = {
            "user_id": event['user_id'],
            "message": message
        }
        await streaming.publish("user.websocket", event)
