"""Blueprints' events."""

import logging

from rampante import streaming, subscribe_on
from sqlalchemy.exc import InterfaceError

from blueprints.build_from_file import CreateFromFile
from blueprints.build_from_s3 import CreateFromS3
from blueprints.models import mBlueprint
from spawner import Spawner

log = logging.getLogger(__name__)


@subscribe_on("service.blueprint.create")
async def create_blueprint(queue, event, app):
    """Task `blueprint.create` events."""
    user_id = event["user_id"]
    user = event["email"].replace("@", "")
    blueprint = event["blueprint"]
    registry = "registry.cassiny.io"

    image_name = f"{registry}/{user}/{blueprint['name']}:{blueprint['tag']}"

    if "path" in event:
        with CreateFromFile(event["path"], blueprint['base_image']) as fo:
            await Spawner.blueprint.create(
                fileobj=fo,
                name=image_name,
            )
    else:
        s3_key = event["s3_key"]
        s3_skey = event["s3_secret"]
        cargo = event["cargo"]

        async with CreateFromS3(
            s3_key=s3_key,
            s3_skey=s3_skey,
            cargo=cargo,
            base_image=blueprint['base_image']
        ) as fo:
            await Spawner.blueprint.create(
                fileobj=fo,
                name=image_name,
            )
    # TODO: fix this part
    # auth = {"username": "barrachri", "password": "empty"}
    #await Spawner.blueprint.push(name=image_name, auth=auth)

    # insert blueprint into db
    try:
        query = mBlueprint.insert().values(
            uuid=event['uuid'],
            repository=f"{registry}/{user}",
            name=blueprint['name'],
            tag=blueprint['tag'],
            user_id=user_id,
            description=blueprint["description"]
        )
        async with app['db'].acquire() as conn:
            await conn.execute(query)
    except InterfaceError:
        raise

    event = {
    }

    await streaming.publish("user.notification", event)
