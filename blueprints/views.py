"""
Blueprints views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
import os
import tarfile
from uuid import uuid4
import aiohttp

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.sql import select

from blueprints.models import mBlueprint
from blueprints.serializers import (
    BlueprintSchema,
    CreateBlueprint,
)
from cargos.models import mCargo
from config import Config as C
from utils import WebView, check_quota, verify_token

log = logging.getLogger(__name__)


class Blueprint(WebView):
    """Views to handle blueprints."""

    @verify_token
    async def get(self, payload):
        """Get blueprints."""
        user_id = payload["user_id"]

        query = select([mBlueprint])\
            .where(
                (mBlueprint.c.public.is_(True)) |
                (mBlueprint.c.user_id == user_id)
        )
        blueprints = await self.query_db(query, many=True)

        blueprint_schema = BlueprintSchema(many=True)
        blueprints, errors = blueprint_schema.dump(blueprints)

        if errors:
            json_response({"error": errors}, status=400)

        return json_response({"blueprints": blueprints})

    @verify_token
    @check_quota(mBlueprint)
    async def post(self, payload):
        """Create blueprints."""
        user_id = payload["user_id"]
        cargo_id = self.request.match_info.get("cargo_id")

        if cargo_id is not None:
            data = await self.request.json()

            blueprint, errors = CreateBlueprint().load(data)
            if errors:
                json_response({"error": errors}, status=400)

            try:
                query = mCargo.delete()\
                    .where(
                    (mCargo.c.user_id == user_id) &
                    (mCargo.c.id == int(cargo_id))
                )
            except ValueError:
                query = mCargo.delete()\
                    .where(
                    (mCargo.c.user_id == user_id) &
                    (mCargo.c.name == cargo_id)
                )

            cargo = await self.query_db(query)

            if cargo is None:
                error = "Did you select the right cargo?"
                return json_response({"error": error}, status=400)

            event = {
                "user_id": user_id,
                "email": payload['email'],
                "token": payload['token'],
                "cargo": cargo.name,
                "s3_key": cargo.specs['access_key'],
                "s3_secret": cargo.specs['secret_key'],
                "blueprint": blueprint
            }
            await streaming.publish("service.create.blueprint", event)

            return json_response({"message": "We are creating your blueprint."})

        #data = await self.request.json()

        #blueprint, errors = CreateBlueprint().load(data)

        ##    json_response({"error": errors}, status=400)

        reader = await self.request.multipart()

        while True:
            part = await reader.next()

            if part is None:
                break

            if part.headers[aiohttp.hdrs.CONTENT_TYPE] == 'application/json':
                data = await part.json()
                blueprint, errors = CreateBlueprint().load(data)
                if errors:
                    json_response({"error": errors}, status=400)
                continue

            file_uuid = f"{uuid4().hex}.tar.gz"
            file_path = os.path.join(C.TEMP_BUILD_FOLDER, file_uuid)

            # You cannot rely on Content-Length if transfer is chunked.
            size = 0
            with open(file_path, 'wb') as f:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)

            if tarfile.is_tarfile(file_path) is False:
                os.remove(file_path)
                return json_response({"error": "No proper file format."}, status=400)

            event = {
                "user_id": user_id,
                "token": payload['token'],
                "path": file_path,
                "blueprint": blueprint
            }

        await streaming.publish("service.blueprint.create", event)

        return json_response({"message": "We are creating your blueprint."})
