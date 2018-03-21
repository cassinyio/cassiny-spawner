"""
Cargos views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


import logging
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming

from cargos.models import delete_cargo, get_cargos
from cargos.serializers import CargoSchema
from spawner import Spawner
from utils import WebView, get_uuid, verify_token

log = logging.getLogger(__name__)


class Cargo(WebView):
    """API endpoint to create, delete and modify cargos."""

    @verify_token
    async def get(self, payload: Mapping[str, Any]):
        """Get a serialized version of the cargo object."""
        user_id = payload['user_id']

        cargos = await get_cargos(self.db, user_id=user_id)
        cargos_schema = CargoSchema(many=True)
        cargos_schema.context = {"user": user_id}

        data, _ = cargos_schema.dump(cargos)

        return json_response({"cargos": data})

    @verify_token
    async def post(self, payload: Mapping[str, Any]):
        """Create a new cargo."""
        user_id = payload['user_id']
        data = await self.request.json()

        data, errors = CargoSchema().load(data)
        if errors:
            log.info(errors)
            return json_response({"message": errors}, status=400)

        event = {
            "uuid": get_uuid().hex,
            "user_id": user_id,
            "data": data
        }

        await streaming.publish("service.cargo.create", event)

        return json_response({"message": f"We are creating your cargo ({event['uuid']})."})

    @verify_token
    async def delete(self, payload: Mapping[str, Any]):
        """Delete a cargo."""
        user_id = payload["user_id"]
        cargo_ref = self.request.match_info.get("cargo_ref")

        deleted_cargo = await delete_cargo(db=self.db, cargo_ref=cargo_ref, user_id=user_id)

        if deleted_cargo is None:
            log.info(f"Cargo doesn't exist inside the database: {cargo_ref}")
            error = "That cargo doesn't exist anymore."
            return json_response({"error": error}, status=400)

        await Spawner.cargo.delete(name=deleted_cargo.name)

        event = {
            "user_id": user_id,
            "name": deleted_cargo.name,
        }

        await streaming.publish("service.cargo.deleted", event)
        message = f"We are removing {deleted_cargo.name}"
        return json_response({"message": message})
