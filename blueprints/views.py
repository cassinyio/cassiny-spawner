"""
Blueprints views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
import os
import tarfile

import aiohttp
from aiohttp.web import json_response
from rampante import streaming

from blueprints.models import (
    delete_blueprint,
    get_blueprint,
    get_blueprints,
)
from blueprints.serializers import (
    BlueprintSchema,
    CreateBlueprint,
    CreateBlueprintFromCargo,
)
from cargos.models import get_cargo
from config import Config
from utils import WebView, get_uuid, verify_token

log = logging.getLogger(__name__)


class Blueprint(WebView):
    """Views to handle blueprints."""

    @verify_token
    async def get(self, payload):
        """Get blueprints."""
        user_id = payload["user_id"]

        rows = await get_blueprints(self.db, user_id=user_id)

        blueprints, errors = BlueprintSchema(many=True).dump(rows)

        if errors:
            json_response({"error": errors}, status=400)

        return json_response({"blueprints": blueprints})

    @verify_token
    async def delete(self, payload):
        """Delete a blueprint."""
        user_id = payload["user_id"]
        data = await self.request.json()

        if 'reference' not in data:
            log.info(f"Blueprint doesn't exist inside the database: {data['reference']}")
            error = "That Blueprint doesn't exist anymore."
            return json_response({"error": error}, status=400)

        blueprint = await delete_blueprint(self.db, blueprint_ref=data['reference'], user_id=user_id)
        if blueprint is None:
            log.info(f"Blueprint doesn't exist inside the database: {data['reference']}")
            error = f"That Blueprint doesn't exist {data['reference']}."
            return json_response({"error": error}, status=400)

        repository = f"{blueprint.repository}/{blueprint.name}"

        event = {
            "uuid": blueprint.uuid,
            "user_id": user_id,
            "repository": repository,
            "tag": blueprint.tag
        }

        await streaming.publish("service.blueprint.deleted", event)
        message = f"We are removing the blueprint {repository}:{blueprint.tag}"
        return json_response({"message": message})


class BuildFromS3(WebView):
    """View to build blueprints using S3."""

    @verify_token
    async def post(self, payload):
        """Create blueprints."""
        user_id = payload["user_id"]
        data = await self.request.json()

        blueprint, errors = CreateBlueprintFromCargo().load(data)
        if errors:
            json_response({"error": errors}, status=400)

        cargo = await get_cargo(self.db, user_id=user_id, cargo_ref=blueprint['cargo'])
        if cargo is None:
            error = "Did you select the right cargo?"
            return json_response({"error": error}, status=400)

        base_blueprint = await get_blueprint(self.db, blueprint_ref=blueprint['base_image'], user_id=user_id)
        if base_blueprint is None:
            error = "Did you select the right blueprint?"
            return json_response({"error": error}, status=400)

        base_image = f"{base_blueprint.repository}/{base_blueprint.name}:{base_blueprint.tag}"

        uuid = get_uuid().hex
        event = {
            "uuid": uuid,
            "user_id": user_id,
            "email": payload['email'],
            "cargo": cargo.name,
            "s3_key": cargo.specs['access_key'],
            "s3_secret": cargo.specs['secret_key'],
            "blueprint": blueprint,
            "base_image": base_image,
        }
        await streaming.publish("service.blueprint.create", event)

        return json_response({"message": f"We are creating your blueprint({uuid})."})


class BlueprintFromFolder(WebView):
    """Views to build a blueprint using a uploaded tar.gz."""

    @verify_token
    async def post(self, payload):
        """Create blueprints."""
        user_id = payload["user_id"]
        uuid = get_uuid().hex

        # when passing a file
        reader = await self.request.multipart()

        while True:
            part = await reader.next()

            if part is None:
                break

            if part.headers[aiohttp.hdrs.CONTENT_TYPE] == 'application/json':
                data = await part.json()
                blueprint, errors = CreateBlueprint().load(data)
                if errors:
                    return json_response({"error": errors}, status=400)

                base_blueprint = await get_blueprint(self.db, blueprint_ref=blueprint['base_image'], user_id=user_id)
                if base_blueprint is None:
                    error = "Did you select the right blueprint?"
                    return json_response({"error": error}, status=400)

                continue

            file_uuid = f"{uuid}.tar.gz"
            file_path = os.path.join(Config.TEMP_BUILD_FOLDER, file_uuid)

            await write_file(file_path=file_path, part=part)

            if tarfile.is_tarfile(file_path) is False:
                os.remove(file_path)
                return json_response({"error": "No proper file format."}, status=400)

        base_image = f"{base_blueprint.repository}/{base_blueprint.name}:{base_blueprint.tag}"

        event = {
            "uuid": uuid,
            "user_id": user_id,
            "email": payload['email'],
            "path": file_path,
            "blueprint": blueprint,
            "base_image": base_image
        }

        await streaming.publish("service.blueprint.create", event)

        return json_response({"message": f"We are creating your blueprint({uuid})."})


async def write_file(file_path: str, part) -> None:
    # You cannot rely on Content-Length if transfer is chunked.
    size = 0
    with open(file_path, 'wb') as f:
        while True:
            chunk = await part.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
