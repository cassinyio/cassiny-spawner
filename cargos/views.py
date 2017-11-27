"""
Cargos views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


import logging
from uuid import uuid4

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.sql import select

from cargos import serializers
from cargos.models import mCargo
from probes.models import mProbe
from utils import WebView, naminator, verify_token

log = logging.getLogger(__name__)


class Cargo(WebView):
    """API endpoint to create, delete and modify cargos."""

    @verify_token
    async def get(self, user_id):
        """Get a serialized version of the cargo object."""
        attached_cargos = set()

        async with self.db.acquire() as conn:
            query = select([
                mCargo,
                mProbe.c.id.label("probe_id"),
            ])\
                .where(
                mCargo.c.user_id == user_id,
            )\
                .select_from(
                mCargo
                .outerjoin(mProbe, mProbe.c.cargo_id == mCargo.c.id)
            )
            result = await conn.execute(query)
            cargos = await result.fetchall()

        # used_space = await get_space(host, cargo.id)
        # if not used_space:
        #    message = f"Something went bad while getting info about {cargo.name} :("
        #    body = {"message": message}
        #    return json_response(body, status=400)

        cargos_schema = serializers.CargoSchema(
            only=(
                "id", "name", "access_key",
                "secret_key", "size", "created_at",
                "user_id", 'probe_id'),
            many=True)
        cargos_schema.context = {"user": user_id,
                                 "attached_cargos": attached_cargos}

        data, errors = cargos_schema.dump(cargos)

        if errors:
            return json_response(errors, status=400)

        return json_response({"cargos": data})

    @verify_token
    async def post(self, user_id):
        """POST view to create cargo objects."""
        data = await self.request.json()
        log.debug(f"data inside post request: {data}")

        schema = serializers.CargoSchema().load(data)

        if schema.errors:
            log.warning(
                f"Error while serializing: {schema.errors} from {data}")
            message = "A field is missing :/"
            body = {"message": message}
            return json_response(body, status=400)

        # create a unique name for the cargo
        name = naminator("cargo")

        # create event
        event = {
            "user_id": user_id,
            "event_uuid": uuid4().hex,
            "name": name,
            "description": schema.data["description"],
            "size": schema.data["size"],
        }

        await streaming.publish("service.cargo.create", event)

        message = f"We are preparing your cargo {name}"
        return json_response({"message": message})

    @verify_token
    async def delete(self, user_id):
        """DELETE view to delete cargo objects."""
        cargo_id = self.request.match_info.get("cargo_id")

        async with self.db.acquire() as conn:
            query = mCargo.delete().where(
                (mCargo.c.user_id == user_id) &
                (mCargo.c.id == cargo_id)
            ).\
                returning(
                mCargo.c.name,
                mCargo.c.size,
                mCargo.c.spacedock_id
            )
            result = await conn.execute(query)
            deleted_cargo = await result.fetchone()

        if deleted_cargo is not None:

            user_message = f"We are removing {deleted_cargo.name}"
            body = {"message": user_message}
            return json_response(body)

        message = ("User has tried to remove a cargo that "
                   f"doesn't exist inside the database: {cargo_id}")
        log.error(message)
        user_message = f"It seems that cargo doesn't exist anymore"
        body = {"message": user_message}
        return json_response(body)
