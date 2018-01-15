"""
Cargos views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


import logging
from secrets import token_urlsafe
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.exc import InterfaceError, InternalError
from sqlalchemy.sql import select, update

from cargos.models import mCargo
from cargos.serializers import CargoSchema
from spawner import Spawner
from utils import (
    WebView,
    check_quota,
    naminator,
    verify_token,
)

log = logging.getLogger(__name__)


class Cargo(WebView):
    """API endpoint to create, delete and modify cargos."""

    @verify_token
    async def get(self, payload: Mapping[str, Any]):
        """Get a serialized version of the cargo object."""
        user_id = payload['user_id']
        cargo_id = self.request.match_info.get("cargo_id")

        if cargo_id:
            query = select([mCargo])\
                .where(
                    (mCargo.c.user_id == user_id) &
                    (mCargo.c.id == cargo_id)
            )
            probe = await self.query_db(query)
            log.error(probe)
            probe_schema = CargoSchema()
            probe_schema.context = {"user": user_id}
            data, _ = probe_schema.dump(probe)

            return json_response({"cargo": data})

        query = select([mCargo])\
            .where(
            mCargo.c.user_id == user_id,
        )
        cargos = await self.query_db(query, many=True)
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

        access_key = token_urlsafe(15).upper()
        secret_key = token_urlsafe(30)

        specs = {
            "access_key": access_key,
            "secret_key": secret_key,
            "description": data['description'],
            "size": data.get("size", 10),
            "cpu": 1,
            "ram": 0.5,
        }

        name = naminator("cargo")

        try:
            query = mCargo.insert().values(
                user_id=user_id,
                name=name,
                specs=specs,
            )
            await self.query_db(query, get_result=False)
        except InterfaceError:
            return json_response({"error": errors}, status=400)

        service = await Spawner.cargo.create(
            name=name,
            user_id=user_id,
            specs=specs,
            access_key=access_key,
            secret_key=secret_key,
        )

        if not service:
            try:
                query = update(mCargo).where(
                    mCargo.c.name == name).values(status=3)
                await self.query_db(query, get_result=False)
            except InternalError:
                log.exception(f"Error while saving status for {name}.")
            finally:
                message = f"There's been an error while creating {name}."
                return json_response({"error": message}, status=400)

        message = f"we are creating {name}."
        return json_response({"message": message})

    @verify_token
    async def delete(self, payload: Mapping[str, Any]):
        """Delete a cargo."""
        user_id = payload["user_id"]
        cargo_id = self.request.match_info.get("cargo_id")

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

        async with self.db.acquire() as conn:
            result = await conn.execute(query.returning(mCargo.c.name))
            deleted_cargo = await result.fetchone()

        if deleted_cargo is None:
            error = "That cargo doesn't exist anymore."
            return json_response({"error": error}, status=400)

        result = await Spawner.cargo.delete(name=deleted_cargo.name)
        event = {
            "user_id": user_id,
            "name": deleted_cargo.name,
        }
        await streaming.publish("service.cargo.deleted", event)
        message = f"We are removing {deleted_cargo.name}"
        return json_response({"message": message})
