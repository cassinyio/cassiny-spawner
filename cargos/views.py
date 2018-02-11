"""
Cargos views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


import logging
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming

from cargos.models import get_cargos, mCargo
from cargos.serializers import CargoSchema
from spawner import Spawner
from utils import (
    WebView,
    check_quota,
    get_uuid,
    verify_token,
)

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
    @check_quota(mCargo)
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

        await streaming.publish("service.probe.create", event)
        log.info(f"{event['uuid']}: {event}")

        return json_response({"message": "We are creating your Job."})

    @verify_token
    async def delete(self, payload: Mapping[str, Any]):
        """Delete a cargo."""
        user_id = payload["user_id"]
        cargo_uuid = self.request.match_info.get("cargo_uuid")

        query = mCargo.delete()\
            .where(
            (
                mCargo.c.user_id == user_id) &
                (
                    mCargo.c.uuid == cargo_uuid |
                    mCargo.c.name == cargo_uuid
            )
        )

        deleted_cargo = await self.query_db(query.returning(mCargo.c.name))

        if deleted_cargo is None:
            log.info(f"Cargo doesn't exist inside the database: {cargo_uuid}")
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
