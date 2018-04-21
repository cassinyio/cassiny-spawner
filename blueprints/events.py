"""Blueprints' events."""

import logging

import aiohttp
from rampante import streaming, subscribe_on

from blueprints.build_from_file import CreateFromFile
from blueprints.build_from_s3 import CreateFromS3
from blueprints.models import upsert_blueprint
from config import Config
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
        with CreateFromFile(event["path"], event['base_image']) as fo:
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
            base_image=event['base_image'],
            bucket=blueprint["bucket"],
        ) as fo:
            await Spawner.blueprint.create(
                fileobj=fo,
                name=image_name,
            )

    log.info(f"Pushing image {image_name} to te registry.")
    await Spawner.blueprint.push(
        name=image_name,
        username=Config.REGISTRY_USER,
        password=Config.REGISTRY_PASSWORD
    )

    log.info(f"Saving image {image_name} inside the db.")
    await upsert_blueprint(
        db=app['db'],
        uuid=event['uuid'],
        repository=f"{registry}/{user}",
        name=blueprint['name'],
        tag=blueprint['tag'],
        user_id=user_id,
        description=blueprint["description"]
    )

    event = {
        "user_id": user_id,
        "uuid": event['uuid'],
        "image_name": image_name,
    }

    await streaming.publish("service.blueprint.completed", event)


@subscribe_on("service.blueprint.deleted")
async def remove_image(queue, event, app):
    """Task `blueprint.deleted` events."""

    repository = event['repository']
    tag = event['tag']

    async with aiohttp.ClientSession() as session:
        url = f"{Config.REGISTRY_URI}/{repository}/manifests/{tag}"
        headers = {'content-type': 'application/vnd.docker.distribution.manifest.v2+json'}
        async with session.get(url, headers=headers) as resp:
            digest = resp.headers.get('Docker-Content-Digest')
            if resp.status // 100 == 2 and digest:
                async with session.delete(f"{Config.REGISTRY_URI}/{repository}/manifests/{digest}") as resp:
                    if resp.status // 100 == 2:
                        log.info(f"Image {event['repository']}:{tag} correctly deleted.")
                    else:
                        payload = await resp.json()
                        log.info(f"Impossible to delete image {repository}:{tag}, error_code: {resp.status} {payload}")
            else:
                payload = await resp.json()
                log.info(f"Impossible to delete image {repository}:{tag}, error_code: {resp.status} {payload}")

    await streaming.publish("service.image.removed", event)
